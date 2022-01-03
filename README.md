# aws-inventory
This is a fork of [aws-inventory](https://github.com/janiko71/aws-inventory)
Coding style is very subjective and as much as I loved the code itself, I very much disliked the style (e.g. heavy commenting with hashtags, bloating the files). I don't feel like imposing my own taste on others, so I decided to fork the code and work on it on a side, so I don't have to argue about the hastags :)

I'm also adding elements to the inventory that are useful TO ME, but not necesarily to anyone else - hence, again, a fork rather than pull requests to the main project.

## Pre-requisites
This program needs Python 3.4 or newer. 

AWS CLI must be installed and configured on the system you want to run aws-inventory. You SHOULD use a special account with minimal rights (= those in inventory*.json files). See [wiki](https://github.com/janiko71/aws-inventory/wiki) for more.

Make sure that you have the latest boto3 version. Older versions may lead to signature error with the newest regions or to some malfunction. Further information here : http://docs.aws.amazon.com/general/latest/gr/signature-version-4.html.


