
import boto3
import time
import os 
print("OS_TYPE:", os.getenv("OS_TYPE"))
print("TECHNIQUE_ID:", os.getenv("TECHNIQUE_ID"))
CONTROLLER_INSTANCE_ID = "i-0b15485216174c486"   # <-- replace with your controller instance ID

def lambda_handler(event, context):
    os_type = os.getenv("OS_TYPE")
    technique_id = os.getenv("TECHNIQUE_ID")

    if not os_type or not technique_id:
        return {
            "statusCode": 400,
            "message": "Missing required parameters: os_type, technique_id"
        }

    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')

    # ✅ List all instances and tags for debugging
    all_instances = []
    reservations = ec2.describe_instances()["Reservations"]
    for res in reservations:
        for inst in res["Instances"]:
            all_instances.append({
                "InstanceId": inst["InstanceId"],
                "Tags": inst.get("Tags", [])
            })

    print("All instances and tags:", all_instances)

    # ✅ Filter instances by OS tag
    reservations = ec2.describe_instances(
        Filters=[{'Name': 'tag:OS', 'Values': [os_type]}]
    )["Reservations"]

    if not reservations:
        return {
            "statusCode": 404,
            "message": f"No instance found with OS tag = {os_type}",
            "all_instances": all_instances  # include in response for debugging
        }

    instance = reservations[0]["Instances"][0]

    attack_id = None
    for tag in instance.get("Tags", []):
        if tag["Key"] == "Name":
            attack_id = tag["Value"]
            break

    if not attack_id:
        return {
            "statusCode": 404,
            "message": f"Target instance {instance['InstanceId']} does not have a Name tag",
            "all_instances": all_instances  # include in response
        }

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
            "output": output,
            "all_instances": all_instances  # include for debugging
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "message": "Error running command",
            "error": str(e),
            "all_instances": all_instances  # include for debugging
        }





