import boto3
import time


CONTROLLER_INSTANCE_ID = "i-0b15485216174c486"   # <-- replace with your controller instance ID

def lambda_handler(event, context):
    os_type = event.get("os_type")     
    technique_id = event.get("technique_id")

    if not os_type or not technique_id:
        return {
            "statusCode": 400,
            "message": "Missing required parameters: os_type, technique_id"
        }

    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')

    # ✅ Find instance(s) with the given OS tag
    reservations = ec2.describe_instances(
        Filters=[{'Name': 'tag:OS', 'Values': [os_type]}]
    )["Reservations"]

    if not reservations:
        return {
            "statusCode": 404,
            "message": f"No instance found with OS tag = {os_type}"
        }

    # ✅ Take the first matching instance
    instance = reservations[0]["Instances"][0]

    # ✅ Fetch the Name tag (this becomes attack_id)
    attack_id = None
    for tag in instance.get("Tags", []):
        if tag["Key"] == "Name":
            attack_id = tag["Value"]
            break

    if not attack_id:
        return {
            "statusCode": 404,
            "message": f"Target instance {instance['InstanceId']} does not have a Name tag"
        }

    # ✅ Build attack_range command (runs on controller instance)
    commands = [
        'export AWS_DEFAULT_REGION=us-west-1',
        'cd /home/ubuntu/attack_range',
        f'poetry run python attack_range.py simulate -e ART -te {technique_id} -t {attack_id}'
    ]

    try:
        response = ssm.send_command(
            Targets=[{'Key': 'InstanceIds', 'Values': [CONTROLLER_INSTANCE_ID]}],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': commands},
            Comment='Run Attack Range simulation from Lambda'
        )

        command_id = response['Command']['CommandId']

        # ✅ Poll for result
        output = None
        for _ in range(30):
            time.sleep(1)
            try:
                output = ssm.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=CONTROLLER_INSTANCE_ID
                )
                if output['Status'] in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
                    break
            except ssm.exceptions.InvocationDoesNotExist:
                continue

        return {
            "statusCode": 200,
            "message": "Attack Range simulation triggered",
            "controller_instance_id": CONTROLLER_INSTANCE_ID,
            "target_instance_id": instance["InstanceId"],
            "attack_id": attack_id,
            "technique_id": technique_id,
            "command_id": command_id,
            "output": output
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "message": "Error running command",
            "error": str(e)

        }
    import boto3
import time


CONTROLLER_INSTANCE_ID = "i-0b15485216174c486"   # <-- replace with your controller instance ID

def lambda_handler(event, context):
    os_type = event.get("os_type")     
    technique_id = event.get("technique_id")

    if not os_type or not technique_id:
        return {
            "statusCode": 400,
            "message": "Missing required parameters: os_type, technique_id"
        }

    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')

    # ✅ Find instance(s) with the given OS tag
    reservations = ec2.describe_instances(
        Filters=[{'Name': 'tag:OS', 'Values': [os_type]}]
    )["Reservations"]

    if not reservations:
        return {
            "statusCode": 404,
            "message": f"No instance found with OS tag = {os_type}"
        }

    # ✅ Take the first matching instance
    instance = reservations[0]["Instances"][0]

    # ✅ Fetch the Name tag (this becomes attack_id)
    attack_id = None
    for tag in instance.get("Tags", []):
        if tag["Key"] == "Name":
            attack_id = tag["Value"]
            break

    if not attack_id:
        return {
            "statusCode": 404,
            "message": f"Target instance {instance['InstanceId']} does not have a Name tag"
        }

    # ✅ Build attack_range command (runs on controller instance)
    commands = [
        'export AWS_DEFAULT_REGION=us-west-1',
        'cd /home/ubuntu/attack_range',
        f'poetry run python attack_range.py simulate -e ART -te {technique_id} -t {attack_id}'
    ]

    try:
        response = ssm.send_command(
            Targets=[{'Key': 'InstanceIds', 'Values': [CONTROLLER_INSTANCE_ID]}],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': commands},
            Comment='Run Attack Range simulation from Lambda'
        )

        command_id = response['Command']['CommandId']

        # ✅ Poll for result
        output = None
        for _ in range(30):
            time.sleep(1)
            try:
                output = ssm.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=CONTROLLER_INSTANCE_ID
                )
                if output['Status'] in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
                    break
            except ssm.exceptions.InvocationDoesNotExist:
                continue

        return {
            "statusCode": 200,
            "message": "Attack Range simulation triggered",
            "controller_instance_id": CONTROLLER_INSTANCE_ID,
            "target_instance_id": instance["InstanceId"],
            "attack_id": attack_id,
            "technique_id": technique_id,
            "command_id": command_id,
            "output": output
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "message": "Error running command",
            "error": str(e)
        }
if __name__ == "__main__":
    # Example payload for testing
    test_event = {
        "os_type": "Linux",
        "technique_id": "T1110.001"
    }

    # Call the lambda_handler with None as context
    response = lambda_handler(test_event, None)
    print("Lambda response:", response)

