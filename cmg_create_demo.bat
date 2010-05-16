C:
mkdir C:\cmg_demo
cd C:\cmg_demo
mkdir remote
mkdir cm
mkdir tom

cd remote
call git init --bare component1.git
cd ..\cm
call git clone C:\cmg_demo\remote\component1.git component1
cd component1
call git commit --allow-empty -m "init"
call git push origin HEAD:master
call git push origin HEAD:comp1_br1
call git fetch
call git checkout -b comp1_br1 origin/comp1_br1
echo 1st in component 1 > component1.txt
call git add .
call git commit -m "1st in component 1"
call git push
cd ..\..

cd remote
call git init --bare component2.git
cd ..\cm
call git clone C:\cmg_demo\remote\component2.git component2
cd component2
call git commit --allow-empty -m "init"
call git push origin HEAD:master
call git push origin HEAD:comp2_br1
call git fetch
call git checkout -b comp2_br1 origin/comp2_br1
echo 1st in component 2 > component2.txt
call git add .
call git commit -m "1st in component 2"
call git push
call git tag comp2_tag1
call git push --tags
cd ..\..

cd remote
call git init --bare container.git
cd ..\cm
call git clone C:\cmg_demo\remote\container.git workspace
cd workspace
type nul > _stream
call git add .
call git commit -m "init"
call git push origin HEAD:master
call git push origin HEAD:stream1
call git fetch
call git checkout -b stream1 origin/stream1

echo [DEFAULT] >> _stream
echo     remote_root = C:\cmg_demo\remote >> _stream
echo [comp1] >> _stream
echo     type = git >> _stream
echo     url = %%(remote_root)s\component1.git >> _stream
echo     branch = origin/comp1_br1 >> _stream
echo [folder1\comp2] >> _stream
echo     type = git >> _stream
echo     url = %%(remote_root)s\component2.git >> _stream
echo     tag = comp2_tag1 >> _stream

echo _stream_*>>.gitignore
echo comp1>>.gitignore
echo folder1/comp2>>.gitignore

call git add .
call git commit -m "add 2 components"

call cmg download
call cmg upload

cd ..\..


