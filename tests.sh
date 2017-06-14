./clean.sh
echo "Running 3 tests, each with 10 different feature sets + 1 with no feature filtering"

echo "TEST #1: Enron"
python analyze_corpus.py -e
echo "Testing models..."
python test_model.py -e > results/enron_base.txt
for i in {1..10}
do
    q=$((i * 500))
    python test_model.py -e -f $q > results/enron_$q.txt
done

echo "TEST #1: TREC"
./clean.sh
python analyze_corpus.py -t
echo "Testing models..."
python test_model.py -t > results/trec_base.txt
for i in {1..10}
do
    q=$((i * 500))
    python test_model.py -t -f $q > results/trec_$q.txt
done

echo "TEST #1: Enron + TREC"
./clean.sh
python analyze_corpus.py
echo "Testing models..."
python test_model.py > results/combined_base.txt
for i in {1..10}
do
    q=$((i * 500))
    python test_model.py -f $q > results/combined_$q.txt
done
