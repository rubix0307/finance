WITH vars AS (SELECT
    %(section_id)s AS section_id,
    %(convert_currency_code)s AS convert_currency_code,

	-- DO NOT EDIT
    '2 ' || %(period)s AS period,
	(NOW() - ('1 ' || %(period)s)::interval) AT TIME ZONE 'UTC' AS week_start
	--
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
		WHERE r.section_id = vars.section_id AND r.date >= NOW() - vars.period::interval AND r.is_processed = true
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
		date AT TIME ZONE 'UTC' as date,
		category_id,
		category_name
	FROM items_rate_usd
	INNER JOIN items_second_rate USING (id)
),
converted_items_grouped_2_weeks AS (
	SELECT
		SUM(ci.price_converted) total,
		CASE
			WHEN ci.date > vars.week_start THEN 1
			ELSE 2
		END AS week_num
	FROM converted_items ci
	JOIN vars ON true
	GROUP BY week_num
)


SELECT json_build_object(
    'value', MAX(CASE WHEN week_num = 1 THEN total END),
    'previous_value', MAX(CASE WHEN week_num = 2 THEN total END)
) AS result
FROM converted_items_grouped_2_weeks;



