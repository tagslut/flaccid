from google.cloud import storage


def setup_fake_gcs():
    # Connect to the fake-gcs-server
    client = storage.Client(
        project="fake-project", client_options={"api_endpoint": "http://localhost:8000"}
    )

    # Create a bucket
    bucket_name = "test-bucket"
    bucket = client.bucket(bucket_name)
    bucket.create(location="US")
    print(f"Bucket {bucket_name} created.")

    # Upload test files
    blob1 = bucket.blob("test1.txt")
    blob1.upload_from_string("This is test file 1.")
    print("Uploaded test1.txt.")

    blob2 = bucket.blob("test2.txt")
    blob2.upload_from_string("This is test file 2.")
    print("Uploaded test2.txt.")


if __name__ == "__main__":
    setup_fake_gcs()
