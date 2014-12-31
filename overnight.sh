#export TESTDB="GZ"
#export TESTDB="testdb1"
#python dev.py -t gv_scores --allgt --db $TESTDB
#python dev.py -t gv_test --allgt --db $TESTDB

#export IBSFLAGS='--noqcache --screen'
#export IBSFLAGS='--noqcache --screen --delete-query-cache'
export IBSFLAGS=''


python dev.py -t tune --db PZ_MTEST
python dev.py -t tune --db GZ_ALL
python dev.py -t tune --db GIR_Tanya
python dev.py -t tune --db PZ_Mothers0

# Current best algorithm 

#python dev.py -t small_best --db GZ_ALL --allgt
#python dev.py -t small_best --db PZ_MTEST --allgt
#python dev.py -t small_best --db PZ_Master0 --allgt

#python dev.py -t nsum --db GZ_ALL --allgt
#python dev.py -t nsum --db PZ_MTEST --allgt
#python dev.py -t nsum --db PZ_Master0 --allgt

#python dev.py -t nsum --db GZ_ALL --allgt --vh --fig-dname nsum_hard
#python dev.py -t nsum --db PZ_MTEST --allgt --vh --fig-dname nsum_hard
#python dev.py -t nsum --db PZ_Master0 --allgt --vh --fig-dname nsum_hard

#python dev.py -t vsmany nsum --db GZ_ALL --allgt
#python dev.py -t vsmany nsum --db PZ_MTEST --allgt
#python dev.py -t vsmany nsum --db PZ_Master0 --allgt


# Test if feature weights do something

#python dev.py -t pzmastertest --db PZ_Master0 --allgt 

#python dev.py -t fgweight --db PZ_Master0 --allgt --noqcache
#python dev.py -t fgweight --db GZ_ALL --allgt
#python dev.py -t fgweight --db PZ_MTEST --allgt

## Test if dupvote weights do something

#python dev.py -t dupvote --db PZ_Master0 --allgt --noqcache
#python dev.py -t dupvote --db GZ_ALL --allgt
#python dev.py -t dupvote --db PZ_MTEST --allgt

## Full tests

#python dev.py -t nov6 --db PZ_Master0 --allgt --noqcache
#python dev.py -t nov6 --db GZ_ALL --allgt
#python dev.py -t nov6 --db PZ_MTEST --allgt

#export IBSFLAGS=''
#python dev.py -t smk5 --allgt --db PZ_Master0 $IBSFLAGS
#python dev.py -t smk5 --allgt --db GZ_ALL $IBSFLAGS
#python dev.py -t smk_64k --allgt --db PZ_MTEST $IBSFLAGS
#python dev.py -t smk_128k --allgt --db PZ_MTEST $IBSFLAGS
#python dev.py -t smk5 --allgt --db PZ_MTEST $IBSFLAGS

#python dev.py -t smk7_overnight --allgt --db GZ_ALL $IBSFLAGS
#python dev.py -t smk7_overnight --allgt --db PZ_Master0 $IBSFLAGS --index 0:200
#python dev.py -t smk7_overnight --allgt --db PZ_MTEST $IBSFLAGS

#python dev.py -t featparams_big2 --db PZ_MTEST --allgt
#python dev.py -t featparams_big2 --db GZ_ALL --allgt
#python dev.py -t featparams_big --db PZ_MTEST --allgt
#python dev.py -t featparams_big --db GZ_ALL --allgt

#python dev.py -t smk2 --db PZ_Master0 --allgt


export IBSFLAGS=''

#python dev.py -t smk6_overnight --allgt --db GZ_ALL $IBSFLAGS
#python dev.py -t smk6_overnight --allgt --db PZ_Master0 $IBSFLAGS 
#python dev.py -t smk6_overnight --allgt --db PZ_MTEST $IBSFLAGS

#python dev.py -t smk6_overnight --allgt --db GZ_ALL $IBSFLAGS
#python dev.py -t smk6_overnight --allgt --db PZ_MTEST $IBSFLAGS
#python dev.py -t smk6_overnight --allgt --db PZ_Master0 $IBSFLAGS
