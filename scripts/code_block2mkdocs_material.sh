function dfs(){

	for file in `ls $1`
	do
		if [ -d $1"/"$file ]
		then
			dfs $1"/"$file
		else
			perl -pe 's/^/\t\t/ if /```c\+\+\s*tab=\".*\"/ .. /\n```/' $1"/"$file > test; cat test > $1"/"$file
		fi
	done
}

dfs .
