#!/bin/bash
COGNITO_USER_POOL_ID="ap-northeast-1_gsP5NLNba"
aws cognito-idp list-users --user-pool-id $COGNITO_USER_POOL_ID |
jq -r '.Users | .[] | .Username' |
while read uname; do
  echo "Deleting User $uname";
  aws cognito-idp admin-delete-user --user-pool-id $COGNITO_USER_POOL_ID --username $uname;
done

aws s3api list-buckets --query 'Buckets[?starts_with(Name, `oscarhsu-nctu-bbs-`) == `true`].Name' | jq -r '.[]' |
while read bucket; do
  aws s3 rb s3://$bucket --force
done

aws dynamodb scan \
  --attributes-to-get name \
  --table-name nctu-bbs-boards --query "Items[*]" \
  | jq --compact-output '.[]' \
  | tr '\n' '\0' \
  | xargs -0 -t -I keyItem \
    aws dynamodb delete-item --table-name nctu-bbs-boards --key=keyItem

aws dynamodb scan \
  --attributes-to-get id \
  --table-name nctu-bbs-posts --query "Items[*]" \
  | jq --compact-output '.[]' \
  | tr '\n' '\0' \
  | xargs -0 -t -I keyItem \
    aws dynamodb delete-item --table-name nctu-bbs-posts --key=keyItem

aws dynamodb scan \
  --attributes-to-get name \
  --table-name nctu-bbs-next-id --query "Items[*]" \
  | jq --compact-output '.[]' \
  | tr '\n' '\0' \
  | xargs -0 -t -I keyItem \
    aws dynamodb delete-item --table-name nctu-bbs-next-id --key=keyItem

aws dynamodb scan \
  --attributes-to-get username \
  --table-name nctu-bbs-connection-id --query "Items[*]" \
  | jq --compact-output '.[]' \
  | tr '\n' '\0' \
  | xargs -0 -t -I keyItem \
    aws dynamodb delete-item --table-name nctu-bbs-connection-id --key=keyItem

aws dynamodb scan \
  --attributes-to-get author \
  --table-name nctu-bbs-author-sub --query "Items[*]" \
  | jq --compact-output '.[]' \
  | tr '\n' '\0' \
  | xargs -0 -t -I keyItem \
    aws dynamodb delete-item --table-name nctu-bbs-author-sub --key=keyItem

aws dynamodb scan \
  --attributes-to-get board \
  --table-name nctu-bbs-board-sub --query "Items[*]" \
  | jq --compact-output '.[]' \
  | tr '\n' '\0' \
  | xargs -0 -t -I keyItem \
    aws dynamodb delete-item --table-name nctu-bbs-board-sub --key=keyItem

aws dynamodb scan \
  --attributes-to-get username \
  --table-name nctu-bbs-user-sub --query "Items[*]" \
  | jq --compact-output '.[]' \
  | tr '\n' '\0' \
  | xargs -0 -t -I keyItem \
    aws dynamodb delete-item --table-name nctu-bbs-user-sub --key=keyItem