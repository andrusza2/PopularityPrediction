Two thumbnails per video - svr testing pipeline:

1. getThumnailsList2.py (output is like "fb_first_pref2.txt")
2. getFeatureVectorDump2.py - extract feature-vectors and dump as python pickle
3. net_svr_ave_kfold_gs.py and net_svr_ext_kfold_gs.py - train svr (kfold)