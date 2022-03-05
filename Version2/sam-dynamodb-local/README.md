 


#### Steps
1. Clone this repo and change to the directory 'sam-dynamodb-local'.  
  
2. Start DynamoDB Local by executing the following at the command prompt:  
	*docker run -p 8000:8000 amazon/dynamodb-local*  
    This will run the DynamoDB local in a docker container at port 8000.  

3. At the command prompt, list the tables on DynamoDB Local by executing:  
    *aws dynamodb list-tables --endpoint-url http://localhost:8000*  

4. An output such as the one shown below confirms that the DynamoDB local instance has been installed and running:  
    *{*  
      *"TableNames": []*   
    *}*    

5. At the command prompt, create the PersonTable by executing:  
    *aws dynamodb create-table --cli-input-json file://json/create-person-table.json --endpoint-url http://localhost:8000*  
      
      **Note:** If you misconfigured your table and need to delete it, you may do so by executing the following command:  
        *aws dynamodb delete-table --table-name PersonTable --endpoint-url http://localhost:8000*  

6. At the command prompt, start the local API Gateway instance by executing:  
    *sam local start-api --env-vars json/env.json*  


### Deploying the application
1. Create a S3 bucket for storing SAM deployment artifacts in the us-east-1 region (or a region of your choosing). Please note that you may not use '-' or '.' in your bucket name.  
	*aws s3 mb s3://{s3-bucket-name} --region us-east-1*  
      
2. Create the Serverless Application Model package using CLI.  
	*sam package \  
	--region us-east-1 \  
	--template-file template.yml \  
	--s3-bucket {s3-bucket-name} \  
	--output-template-file packaged.yml*  
      
2. Deploy the packaged template.  
	*aws cloudformation deploy \  
	--region us-east-1 \  
	--template-file packaged.yml \  
	--stack-name {stack_name} \  
	--capabilities CAPABILITY_IAM*  
  
3. After the stack has been successfully created, you may test the application using the CURL commands as shown above.  

