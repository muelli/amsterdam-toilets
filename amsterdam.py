#!/usr/bin/env python
import json
import logging

log = logging.getLogger(__name__)

def load_json(fname="toilets.geojson"):
    data = json.load(open(fname))
    features = data["features"]
    for feature in features:
        osm_feature = {}
        osm_feature["geometry"] = feature["geometry"]

        osm_props = {}
        osm_props["amenity"] = "toilet"
        osm_props["access"] = "yes"

        properties = feature["properties"]
        osm_props["description"] = properties["Omschrijving"]

        feature["fee"] = "no" if properties["Prijs_per_gebruik"] == "0" else "yes"

        selectie = properties["SELECTIE"]
        if selectie == "KRUL":
            osm_props["male"] = "yes"
            osm_props["female"] = "no"
            osm_props["toilets:disposal"] = "pitlatrine"
            osm_props["toilets:position"] = "urinal"

        elif selectie == "TOEGANG":
            # accessible for disabled, e.g. Stadsloket, so in a building. But others exist, too.
            # This probably requires more elaborate logic to tag the building
            # But then again, it might be good to know where exactly the toilet is (in the building)
            # A separate node is also good for finding the level of the toilet
            osm_props["wheelchair"] = "yes"

        elif selectie == "URILIFT":
            # These typically have opening hours
            osm_props["male"] = "yes"
            osm_props["female"] = "no"
            osm_props["toilets:disposal"] = "pitlatrine"
            osm_props["toilets:position"] = "urinal"

        elif selectie == "OVERIG":
            # They describe it as "overig urinoir", so we assume it's a latrine
            if properties["Soort"] != "Overig urinoir (m)":
                log.warning("Sort is " + properties["Soort"])
            osm_props["male"] = "yes"
            osm_props["female"] = "no"
            osm_props["toilets:disposal"] = "pitlatrine"
            osm_props["toilets:position"] = "urinal"

        elif selectie == "OPENBAAR":
            # These typically have opening hours
            osm_props["toilets:disposal"] = "pitlatrine"
            osm_props["toilets:position"] = "urinal"

        elif selectie == "PARKEER":
            # This is a toilet in a parking garage
            # It would probably be good to tag the relationship to the garage node
            # A separate node is also good for finding the level of the toilet
            pass

        elif selectie == "SEIZOEN":
            # What is this? Maybe seasonal.
            log.debug("We don't know yet what SEIZON is")
            continue
            osm_props["toilets:disposal"] = "pitlatrine"
            osm_props["toilets:position"] = "urinal"

        elif selectie == "ONZEKER":
            # This seems to be "not sure"
            log.debug("We skip 'ONZEKER'")
            continue

        elif selectie == "GEWENST":
            # This seems to be "hope for", i.e. planned for the future
            log.debug("We skip 'GEWENST'")
            continue

        elif selectie == "VERDWENEN":
            # This seems to be "disappeared", i.e. it does not exist any more
            log.debug("We skip 'VERDWENEN'")
            continue

        else:
            raise NotImplementedError("Selectie " + selectie + " not known")

        hours = properties["Openingstijden"]
        days = properties["Dagen_geopend"]
        if    hours == "" and days == "" \
           or "24 uur" in str(hours) \
           or hours == 24 \
           or days == "di - do - ma - vr - wo - za - zo" and hours == "":
            # This means 24/7
            osm_props["opening_hours"] = "24/7"
        else:
            log.warning("days: %s, hours: %s", days, hours)
            osm_props["description"] += "\r\n"
            osm_props["description"] += "\r\n".join((days, hours))

        if False:
            sort = properties["Soort"]
            if sort == "Seizoen (m/v)":
                pass
            elif sort == "Openbaar toilet (m/v)":
                pass
            else:
                raise NotImplementedError("Sort " + sort + " not known")

        for prop in properties:
            pass

        if osm_props["description"] == "" or osm_props["description"] == "Parkeergarage":
            del osm_props["description"]

        osm_feature["properties"] = osm_props
        yield osm_feature

def main():
    logging.basicConfig(level=logging.INFO)
    features = list(load_json("toilets.geojson"))
    for feature in features:
        pass
        #print (feature)
    geojson = {
        "type": "FeatureCollection",
        "name": "Public Toilets of Amsterdam",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84",
            }
        }
    }
    geojson["features"] = features
    print (json.dumps(geojson, indent=4))

if __name__ == "__main__":
    main()
