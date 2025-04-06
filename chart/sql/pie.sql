WITH vars AS (SELECT
    %(section_id)s AS section_id,
    %(convert_currency_code)s AS convert_currency_code,
    %(period)s AS period
),

items_rate_usd AS (
    SELECT id,name,price, rate_per_usd,receipt_id,date,currency_id,time_diff,rate_date, category_id, category_name
    FROM (
        SELECT
            ri.id,
            ri.name,
            ri.price,
            ri.receipt_id,
            r.date AT TIME ZONE 'UTC' AS date,
            r.currency_id,
			ric.id AS category_id,
			ric.name AS category_name,
			CASE 
			    WHEN r.currency_id = 'USD' THEN 1 
			    ELSE crh.per_usd
			END AS rate_per_usd,
            ABS(EXTRACT(EPOCH FROM (crh.date AT TIME ZONE 'UTC' - r.date AT TIME ZONE 'UTC')))::numeric(10, 0) AS time_diff,
            crh.date AT TIME ZONE 'UTC' rate_date,
            ROW_NUMBER() OVER (PARTITION BY ri.id ORDER BY ABS(EXTRACT(EPOCH FROM (crh.date AT TIME ZONE 'UTC' - r.date AT TIME ZONE 'UTC'))) ASC) AS rn
        FROM receipt_item ri
        INNER JOIN receipt r ON r.id = ri.receipt_id
		INNER JOIN receipt_item_category ric ON ri.category_id = ric.id
        LEFT JOIN currency_rate_history crh ON r.currency_id = crh.currency_id
		JOIN vars ON true
		WHERE r.section_id = vars.section_id AND r.date >= NOW() - vars.period::interval
    ) AS ranked_items
    WHERE rn = 1
),

items_second_rate AS (
	SELECT id, second_rate_per_usd, second_currency_id FROM (SELECT
		DISTINCT irusd.id,
		crh.per_usd second_rate_per_usd,
		crh.currency_id second_currency_id,
		ABS(EXTRACT(EPOCH FROM (crh.date AT TIME ZONE 'UTC' - irusd.date AT TIME ZONE 'UTC')))::numeric(10, 0) AS time_diff,
		ROW_NUMBER() OVER (PARTITION BY irusd.id ORDER BY ABS(EXTRACT(EPOCH FROM (crh.date AT TIME ZONE 'UTC' - irusd.date AT TIME ZONE 'UTC'))) ASC) AS rn
	FROM items_rate_usd irusd
		JOIN vars ON true
		INNER JOIN currency_rate_history crh ON crh.currency_id = vars.convert_currency_code
		ORDER BY irusd.id, rn) AS ranked_items
	WHERE rn = 1	
),


converted_items AS (
	SELECT
		id,
		receipt_id,
		name,
		price price_original,
		((price / rate_per_usd) * second_rate_per_usd)::numeric(10, 2) price_converted,
		currency_id currency_id_original,
		second_currency_id currency_id_converted,
		date,
		category_id,
		category_name
	FROM items_rate_usd
	INNER JOIN items_second_rate USING (id)
),

grouped_converted_items_by_category_and_currency AS (
	SELECT 
		category_id,
		currency_id_original,
		SUM(price_original) AS total_price_original,
		SUM(price_converted) AS total_price_converted 
	FROM converted_items
	GROUP BY category_id, currency_id_original
), 

pie_data AS (
	SELECT 
	  category_id,
	  SUM(total_price_converted) AS value,
	  json_object_agg(
	    currency_id_original,
	    json_build_object(
	      'original', total_price_original,
	      'converted', total_price_converted
	    )
	  ) AS currencies
	FROM grouped_converted_items_by_category_and_currency
	GROUP BY category_id
)

SELECT 
	pd.category_id,
	ric.name AS category_name,
	ric.color AS category_color,
	pd.value,
	pd.currencies
FROM pie_data pd
INNER JOIN receipt_item_category ric ON ric.id = pd.category_id 












