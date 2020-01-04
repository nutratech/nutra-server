:;
:;
:; # Run Flask locally, and pointi to local PostgreSQL server
:;


:; # -- BASH -- #
:; cd db
:; ./local.cmd &
:; cd ..
:; ./server.py
:; exit


:; # - cmd.exe - #
cd db
./local.cmd &
cd ..
./server.py
python server.py
