provider "aws" {
  region = "us-east-1"
}

resource "random_pet" "name" {
  length = 2
  prefix = "zeako"
}

resource "aws_s3_bucket" "inventory" {
  bucket = "${random_pet.name.id}"
  acl    = "private"

  lifecycle_rule {
    id      = "frames"
    enabled = true

    prefix = "frames/"

    transition {
      storage_class = "INTELLIGENT_TIERING"
    }
  }
}

resource "aws_s3_bucket_notification" "object_created" {
  bucket = "${aws_s3_bucket.inventory.id}"

  queue {
    queue_arn = "${aws_sqs_queue.event_notification.arn}"
    events    = ["s3:ObjectCreated:Put"]

    filter_prefix = "frames/"
  }
}

resource "aws_sqs_queue" "event_notification" {
  name = "${random_pet.name.id}"

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:*:*:${random_pet.name.id}",
      "Condition": {
        "ArnEquals": { "aws:SourceArn": "${aws_s3_bucket.inventory.arn}" }
      }
    }
  ]
}
POLICY
}

resource "aws_sns_topic" "plant_detection" {
  name = "${random_pet.name.id}"
}

# we use sms because email isn't supported via terraform
resource "aws_sns_topic_subscription" "email" {
  topic_arn = "${aws_sns_topic.plant_detection.arn}"
  protocol  = "sms"
  endpoint  = "" # valid phone number, e.g +972545555555
}
