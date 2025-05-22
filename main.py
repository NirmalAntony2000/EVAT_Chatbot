    elif intent == "SelectCharger":
        user_input = data['queryResult']['queryText'].strip().lower()
        context = next((ctx for ctx in data['queryResult']['outputContexts']
                        if 'awaiting_selection' in ctx['name']), {})
        charger_list = context.get("parameters", {}).get("chargers", [])
        
        selected = next(
            (c for c in charger_list if c["label"].strip().lower() == user_input),
            None
        )

        if not selected:
            return {"fulfillmentText": f"Sorry, the charger '{user_input}' wasn't recognized. Please try again."}

        lat = selected.get("lat")
        lon = selected.get("lon")
        label = selected.get("label")

        try:
            nearby_chargers = get_chargers(lat, lon)
            other_chargers = []
            for c in nearby_chargers:
                info = c.get("AddressInfo", {})
                title = info.get("Title", "")
                line1 = info.get("AddressLine1", "")
                combined = f"{title} – {line1}".strip()
                if combined.lower() != label.lower():
                    other_chargers.append(combined)
        except Exception:
            other_chargers = []

        reply = f"You selected: {label}.\n"
        if other_chargers:
            reply += "Here are other chargers nearby:\n"
            reply += "\n".join(f"- {c}" for c in other_chargers[:3])
        else:
            reply += "No other chargers found nearby."
        
        reply += "\n\nWould you like to see nearby cafés, restrooms, or convenience stores?"

        return {
            "fulfillmentText": reply,
            "fulfillmentMessages": [{
                "quickReplies": {
                    "title": "Choose a place type:",
                    "quickReplies": ["cafes", "restrooms", "convenience stores"]
                }
            }],
            "outputContexts": [{
                "name": f"{data['session']}/contexts/awaiting_amenity_type",
                "lifespanCount": 5,
                "parameters": {
                    "selected": selected
                }
            }]
        }
