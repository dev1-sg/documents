bootstrap cdk

```bash
cdk bootstrap --qualifier d1sg-ecr
```

deploy cdk

```bash
cdk deploy
```

query base images

```
aws lambda invoke --function-name EcrPublicLambda-base d1sg-image-list-base.json
```

query ci images

```
aws lambda invoke --function-name EcrPublicLambda-ci d1sg-image-list-ci.json
```
