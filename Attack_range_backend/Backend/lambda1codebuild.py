import boto3
import json

codebuild = boto3.client("codebuild")

def lambda_handler(event, context):
    try:
        # Here `event` is passed directly (no body wrapper)
        os_type = event.get("os_type")
        technique_id = event.get("technique_id")

        if not os_type or not technique_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing os_type or technique_id"})
            }

        response = codebuild.start_build(
            projectName="arcode",
            environmentVariablesOverride=[
                {"name": "OS_TYPE", "value": os_type, "type": "PLAINTEXT"},
                {"name": "TECHNIQUE_ID", "value": technique_id, "type": "PLAINTEXT"}
            ]
        )

        build_id = response["build"]["id"]

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Attack started",
                "build_id": build_id
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
