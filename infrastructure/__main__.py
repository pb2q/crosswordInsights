

"""An AWS Python Pulumi program"""

import sys

import pulumi
import pulumi_aws

from pulumi_aws import iam
from pulumi_aws import s3
from pulumi_aws import dynamodb
from pulumi_aws import ecs


print(sys.path)


# Create an AWS resource (S3 Bucket)
bucket = s3.Bucket('nyt-crossword-files')

# Export the name of the bucket
pulumi.export('bucket_name', bucket.id)


# Example of the stats that come from the NYT API call:
# 'eligible': True, 'firstOpened': 1661171700, 'firstSolved': 1661172023,
# 'id': '71192877-20331', 'isPuzzleInfoRead': False, 'lastUpdateTime': 1661172024,
# 'solved': True, 'completed': True, 'timeElapsed': 323, 'epoch': 1661171707
#
# Example of data file produced from
#   https://github.com/mattdodge/nyt-crossword-stats
# 
# date,day,elapsed_seconds,solved,checked,revealed,streak_eligible
# 2022-08-22,Mon,323,1,0,0,1

# create a DynamoDB table to hold the basic stats:
# Non-key or index attributes:
#   
# "ElapsedSeconds"  "N"
# "IsSolved" "S"
# "UsedHelp" "S"
# "StreakEligible" "S"
# "FirstOpened" "N"
# "FirstChecked" "N"
# "FirstRevealed" "N"
# "FirstSolved" "N"
# "Id" "S"
db = dynamodb.Table("CrosswordStats",
      attributes = [
         dynamodb.TableAttributeArgs(
            name = "UserId",
            type = "S",
         ),
         dynamodb.TableAttributeArgs(
            name = "Date",
            type = "S",
         ),
         dynamodb.TableAttributeArgs(
            name = "DayOfWeek",
            type = "S",
         ),
      ],
      hash_key = "UserId",
      range_key = "Date",
      local_secondary_indexes = [
           dynamodb.TableLocalSecondaryIndexArgs(
              range_key = "DayOfWeek",
              name = "DayOfWeekIndex",
              projection_type = "KEYS_ONLY"
           )
      ],
      tags = {
         "Environment": pulumi.get_stack()
      },
      read_capacity = 10,
      write_capacity = 10,
      stream_enabled = True,
      stream_view_type = "KEYS_ONLY"
   )


# Build the ID fetch lambda using a containerfile
#repo = ecs.Repository("crossword-insights")

#image = ecs.Image("image", repository_url=repo.url,
#                  path="../src/fetchPuzzleIds")

