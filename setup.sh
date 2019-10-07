sudo apt update
sudo apt install python3-pip

pip3 install efficiency requests tqdm lxml
tmux
mkdir temp
cd temp
curl -O https://raw.githubusercontent.com/zhijing-jin/crawler/master/bitly_get_clicks.py
python3 bitly_get_clicks.py -len 3 -shard 8
python3 bitly_get_clicks.py -len 4 -use_proxy -proxy_file proxies2.txt -shard 2
