# Thanks to Thamme Gowda on Stack Overflow 
# Link: https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script?page=1&tab=scoredesc#tab-top

python3 $(dirname -- ${BASH_SOURCE[0]})/black_1.py
