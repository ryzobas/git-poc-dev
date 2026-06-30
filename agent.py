import boto3
from botocore.exceptions import BotoCoreError, ClientError


class S3ApiClient:
    """Simple S3 API client for listing objects in a bucket."""

    def __init__(self, region_name=None):
        self.s3_client = boto3.client("s3", region_name=region_name)

    def list_objects(self, bucket_name, prefix=None, max_keys=1000):
        """List all objects in an S3 bucket optionally filtered by prefix.

        Returns a list of object metadata dictionaries.
        """
        paginator = self.s3_client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(
            Bucket=bucket_name,
            Prefix=prefix or "",
            PaginationConfig={"PageSize": max_keys},
        )

        objects = []
        try:
            for page in page_iterator:
                contents = page.get("Contents", [])
                for item in contents:
                    objects.append({
                        "Key": item["Key"],
                        "Size": item["Size"],
                        "LastModified": item["LastModified"],
                        "StorageClass": item.get("StorageClass"),
                    })
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError(f"Failed to list objects in bucket '{bucket_name}': {exc}") from exc

        return objects


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="List objects in an S3 bucket.")
    parser.add_argument("bucket", help="The name of the S3 bucket")
    parser.add_argument("--prefix", help="Optional prefix to filter objects", default="")
    parser.add_argument("--region", help="AWS region of the bucket", default=None)
    args = parser.parse_args()

    client = S3ApiClient(region_name=args.region)
    try:
        object_list = client.list_objects(args.bucket, prefix=args.prefix)
        for obj in object_list:
            print(f"{obj['Key']}\t{obj['Size']}\t{obj['LastModified']}\t{obj['StorageClass']}")
    except RuntimeError as error:
        print(error)
        raise
