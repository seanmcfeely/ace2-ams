import argparse
import cProfile
import time

from sqlalchemy.orm import Session

from database import get_db
from tests import factory


def run(args):
    # When you specify the path to the JSON file, you do so from the perspective
    # of outisde the container, so you preface it with db/ so that you can
    # use tab-completion on your local command line.
    #
    # However, this runs inside of the container, so the db/ part of the path
    # does not exist and must be removed so that it is a valid path inside the container.
    #
    # Example: db/app/tests/alerts/blah.json -> /app/tests/alerts/blah.json
    start = time.time()
    json_path = args.alert_json_path.replace("db", "")

    db: Session = next(get_db())

    for i in range(args.num_alerts):
        factory.submission.create_from_json_file(db=db, json_path=json_path, submission_name=f"Manual Alert {i}")

    print(f"Inserted {args.num_alerts} alerts in {time.time() - start} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Required
    parser.add_argument("alert_json_path", type=str, help="Path to the alert JSON template file to add")

    # Optional
    parser.add_argument("--num_alerts", type=int, default=1, help="The number of copies of the alert to add")
    parser.add_argument(
        "--profile",
        action="store_true",
        default=False,
        help="Uses cProfile and outputs stats file to insert_alert_<JSON_FILE_NAME>.stats",
    )

    args = parser.parse_args()

    if args.profile:
        cProfile.run("run(args)", f"insert_alert_{args.alert_json_path.split('/')[-1]}.stats")
    else:
        run(args)
