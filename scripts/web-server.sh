. config/set_env.bash
. server/venv/bin/activate
rm -f /tmp/worker.py-*
cd server
export PATH=$PATH:venv/bin/
python setup.py install
foreman start
