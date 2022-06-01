resource "aws_s3_bucket" "file_storage_bucket" {
  bucket = "ice2-file-storage"

  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "file_storage_encryption" {
  bucket = aws_s3_bucket.file_storage_bucket.bucket
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.ice2_s3.arn
        sse_algorithm     = "aws:kms"
      }
    }
}

resource "aws_s3_bucket_policy" "allow_access_from_own_account" {
  bucket = aws_s3_bucket.file_storage_bucket.id
  policy = data.aws_iam_policy_document.allow_access_from_own_account.json
}

data "aws_iam_policy_document" "allow_access_from_own_account" {
  statement {
    principals {
      type        = "AWS"
      identifiers = [data.aws_caller_identity.current.account_id]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
      "s3:PutObject"
    ]

    resources = [
      aws_s3_bucket.file_storage_bucket.arn,
      "${aws_s3_bucket.file_storage_bucket.arn}/*",
    ]
  }
}