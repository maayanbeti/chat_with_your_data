# Rule: visualization_output

Apply the following chart-selection rules in order.

1. Use a table when the user asks: top, list, show me, compare exact values, details, rows, flights by airline.
2. Use a bar chart when comparing categories.
- Which airlines have the most flights?
- Flights by country
- Top destinations
3. Use a donut chart when asking for part-to-whole share.
- Distribution of airlines by percentage
- What share of flights are departures vs arrivals?
4. Use a line chart when time is involved.
- Flights over time
- How many flights per hour?
- Daily trend by airline
5. Use KPI cards for single-number questions, including any rate questions.
- How many flights are there?
- How many delayed flights?
- What percentage departed on time?
- What is the cancellation rate?
- What is the on-time rate?
- What is the delay rate?
Rate questions must always include a visual indicator: a directional arrow, a color (green/red based on polarity), and a formatted percentage value.
6. Use a stacked bar chart for category split by another category.
- Arrival vs departure by airline
- Status distribution by terminal

Comment: if there are more than 6-8 categories, use a bar chart or group small categories into Other.
Comment: display both absolute values and percentages on donut labels.
Comment: rate questions (cancellation rate, on-time rate, delay rate, etc.) always display a KPI indicator — formatted as a percentage with a directional arrow and polarity color (green = good direction, red = bad direction).
