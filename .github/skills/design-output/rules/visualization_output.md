# Rule: visualization_output

Apply the following chart-selection rules in order.

1. Use a table when the user asks: top, list, show me, compare exact values, details, rows, flights by airline.
2. Use a bar chart when comparing categories.
- Which airlines have the most flights?
- Flights by country
- Top destinations
- A rate broken down per category (e.g. "on-time rate per airline") — each category's
  rate is independent and doesn't sum to a whole, so it stays a bar chart, not a donut.
3. Use a donut chart when asking for part-to-whole share.
- Distribution of airlines by percentage
- What share of flights are departures vs arrivals?
- A status-filtered subset (cancellations, delays, etc.) broken down by count into
  another category, e.g. "Canceled flights by destination country", "Delayed flights
  by airline" — this is checked *before* the general "by X" bar-chart rule, because
  the count breakdown of a filtered subset is a share of that subset (sums to 100%
  of the subset), unlike an unfiltered "flights by country" magnitude comparison.
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
6. Use an animated map when asking for the closest/nearest/soonest/next/top N/present/show me flights to or from a place.
- Present me the closest top 5 flights to America and the expected time to arrive
- What are the next 5 flights to Europe?
- What are the nearest flights to Paris and when will they land?
- Show me the flights to Cyprus and their arrival time
- Present the flights to Japan
- Checked before the plain "top N" table rule — pairing a ranking/presenting
  word ("closest", "nearest", "soonest", "next", "top", "present", "show me")
  with a route direction (" to "/" from ") turns a list request into a
  route-animation request, even if the question doesn't say "arrival"/"eta"
  explicitly — the expected arrival time is always part of this view, not
  conditional on being asked. "Top 5 destinations" alone (no " to "/" from ")
  stays a table/bar chart.
- Expected arrival time = departure `scheduled_dt` (from BGN) + the
  destination country's `avg_flight_hours_estimate` (see
  `.github/skills/flight-route-duration/SKILL.md`) — always label that as an
  estimate, not a measured arrival time.
7. Use a stacked bar chart for category split by another category.
- Arrival vs departure by airline
- Status distribution by terminal

Comment: if there are more than 6-8 categories, use a bar chart or group small categories into Other.
Comment: display both absolute values and percentages on donut labels.
Comment: rate questions (cancellation rate, on-time rate, delay rate, etc.) always display a KPI indicator — formatted as a percentage with a directional arrow and polarity color (green = good direction, red = bad direction).
