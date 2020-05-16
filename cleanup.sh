#!/bin/bash
COGNITO_USER_POOL_ID=" us-west-2_eAO87HoYF"
aws cognito-idp list-users --user-pool-id $COGNITO_USER_POOL_ID |
jq -r '.Users | .[] | .Username' |
while read uname; do
  echo "Deleting User $uname";
  aws cognito-idp admin-delete-user --user-pool-id $COGNITO_USER_POOL_ID --username $uname;
done

# aws s3api list-buckets --query 'Buckets[?starts_with(Name, `oscarhsu-nctu-bbs-`) == `true`].Name' | jq -r '.[]' |
# while read bucket; do
#   aws s3 rb s3://$bucket --force
# done

# aws dynamodb list-tables | jq -r '.TableNames | .[] | select(startswith("oscarhsu-nctu-bbs"))' |
# while read table; do
#   echo "Deleting Table $table";
#   aws dynamodb delete-table --table-name $table > /dev/null 2>&1
# done