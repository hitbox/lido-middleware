#!

logdir=instance/logging

tail $logdir/central_load_plan.log

for fn in paxdetail.log pistol2.log sable2.log; do
	echo $fn
	grep 'processing message' $logdir/$fn | tail
done

