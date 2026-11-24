TEL-D5-502: Lambda Timeouts: Logs Insights Meets X-Ray              Suggested time: 75 min
===============================================================================
YOU NEED: browser, AWS sandbox account (CloudFormation, Lambda, S3, CloudWatch, X-Ray, EC2 read access),
your seat id (u01-u40), and from the instructor: SubnetIds and SecurityGroupId of the shared VPC.
No CLI. Everything runs in the AWS Management Console. Use the region the instructor names.

OBSERVED FAILURE
  Order invoice generation Lambdas terminate abruptly with 'Task timed out after 30.00 seconds'.
  CloudWatch logs show timeouts but do not reveal the stalled downstream call.

STEP 1 - DEPLOY (5 min)
  CloudFormation -> Create stack (new resources) -> Upload template: starter/aws/invoice-stack.yaml
  Stack name: invoice-s2-<seat>   Parameters: Seat = <seat>, SubnetIds = <from instructor>, SecurityGroupId = <from instructor>
  Tick the IAM acknowledgement -> Submit -> wait for CREATE_COMPLETE (about 2 min).
  The function invoice-generator-<seat> starts every minute (EventBridge schedule). Wait 3 minutes for data.

STEP 2 - LOGS (CloudWatch -> Logs Insights, log group /aws/lambda/invoice-generator-<seat>, last 30 min)
    fields @timestamp, @message, @requestId
    | filter @message like /Task timed out/
    | sort @timestamp desc
    | limit 20
  Pick one @requestId. Then show every line of that request:
    fields @timestamp, @message
    | filter @requestId = "<request id>"
    | sort @timestamp asc
  (If @requestId is not offered: parse @message /(?<req>[0-9a-f-]{36})/ ). Note the trace_id in the JSON line "generating invoice".
  What do the logs tell you about WHAT was slow? (Nothing - that is the point.)

STEP 3 - TRACE (CloudWatch -> X-Ray traces -> Traces, or X-Ray -> Traces; search the trace id)
  Open the trace waterfall: segments of the function, subsegments render-invoice and S3:PutObject.
  Record the duration of S3:PutObject (about 29.7 s) and the bucket annotation.

STEP 4 - ROOT CAUSE (console only)
  Lambda -> invoice-generator-<seat> -> Configuration -> VPC: which subnets? Open one -> Route table.
  VPC -> Endpoints: is there a gateway endpoint for com.amazonaws.<region>.s3? Which routes does the private route table have?
  Write the root cause in evidence_D5_2.md.

STEP 5 - FIX AND VERIFY
  The VPC is shared: your instructor applies the fix (adds the S3 gateway endpoint to the private route table).
  Wait for "go", then wait 2-3 minutes and re-run the Step 2 queries for the newest invocations:
  the log line "invoice stored" must appear and S3:PutObject must be well under 1 s.

SUBMISSION & EVIDENCE
  1. Fill in starter/evidence/evidence_D5_2.md
  2. Validate:   .\validation_script.ps1 check   (Linux/macOS: ./validation_script.sh check)

CLEAN UP (after sign-off): S3 -> open the bucket shopnow-invoices-archive-<seat>-<account id> -> Empty,
  then CloudFormation -> delete stack invoice-s2-<seat>.
===============================================================================
