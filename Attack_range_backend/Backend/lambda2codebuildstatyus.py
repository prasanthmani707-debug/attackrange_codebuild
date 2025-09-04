import boto3
import json
import urllib.parse

codebuild = boto3.client("codebuild")

def lambda_handler(event, context):
    try:
        print("Incoming event:", json.dumps(event))

        build_id = None

        # Case 1: Query string (GET /attack-status?build_id=xxx)
        if "queryStringParameters" in event and event["queryStringParameters"]:
            build_id = event["queryStringParameters"].get("build_id")

        # Case 2: POST body (JSON)
        if not build_id and "body" in event and event["body"]:
            body = json.loads(event["body"])
            build_id = body.get("build_id")

        # Case 3: Direct payload (non-proxy integration)
        if not build_id and "build_id" in event:
            build_id = event["build_id"]

        if not build_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing build_id"})
            }

        # Fetch build info
        response = codebuild.batch_get_builds(ids=[build_id])

        if not response["builds"]:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Build ID not found"})
            }

        build_info = response["builds"][0]

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "build_id": build_id,
                "status": build_info["buildStatus"],
                "currentPhase": build_info.get("currentPhase"),
                "startTime": str(build_info.get("startTime")),
                "endTime": str(build_info.get("endTime"))
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
