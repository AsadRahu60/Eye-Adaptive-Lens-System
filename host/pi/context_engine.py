def classify(d,l,m): return 'near' if d and d<60 else 'outdoor' if l and l>5000 else 'desk'
