import boto3
import json

codebuild = boto3.client("codebuild")

def lambda_handler(event, context):
    try:
        # Event will be a simple JSON with build_id
        build_id = event.get("build_id")
        if not build_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing build_id"})
            }

        response = codebuild.batch_get_builds(ids=[build_id])

        if not response["builds"]:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Build ID not found"})
            }

        build_info = response["builds"][0]
        build_status = build_info["buildStatus"]

        return {
            "statusCode": 200,
            "body": json.dumps({
                "build_id": build_id,
                "status": build_status,
                "startTime": str(build_info.get("startTime")),
                "endTime": str(build_info.get("endTime")),
                "currentPhase": build_info.get("currentPhase")
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
