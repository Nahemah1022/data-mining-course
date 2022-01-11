import pandas as pd
import random
import argparse

CONTINUOUS = 4
BINARY = 4

# X[:, :INFORMATIVE + CORELATED + IRRELEVANT]

def parse_arg():
    parser = argparse.ArgumentParser(
        prog='python generator.py',
        description='Generate data with specific class by absolute right rules.',
    )
    parser.add_argument(
        '--irrelevant',
        help='Number of irrelevant attributes.',
        type=int,
        default=0,
    )
    parser.add_argument(
        '--use_bmi',
        help='To use BMI attribute or not.',
        type=bool,
        default=False,
    )
    parser.add_argument(
        '--dependent',
        help='Number of dependent attributes.',
        type=int,
        default=1,
    )
    parser.add_argument(
        '--binary',
        help='Number of binary attributes.',
        type=int,
        default=4,
    )
    parser.add_argument(
        '--use_linear',
        help="To generate rule by attribute's linear comnibation or not.",
        type=bool,
        default=False,
    )

    return parser.parse_args()

def rule_match(arg, data):
    cnt = 0
    if (arg.use_linear):
        res = data[0] - 100 * data[2] + 2 * data[3]
        if (res < 300 or res > 450):
            cnt = cnt + 1
    else:
        if (data[0] > 196 or data[0] < 155): 
            cnt = cnt + 1
        if (data[2] < 0.1):
            cnt = cnt + 1
        if (data[3] < 85):
            cnt = cnt + 1

        if (arg.use_bmi):
            bmi = (data[1] / ((data[0] / 100) ** 2))
            if (bmi < 16.5 or bmi > 31.5):
                cnt = cnt + 1
        
    for i in range(arg.binary):
        if (data[CONTINUOUS + i] != 0):
            cnt = cnt + 1

    return cnt < arg.dependent

def gen_data(arg, bin_positive = False):
    data = [
        random.randrange(140, 220), 
        random.randrange(30, 130), 
        round(random.uniform(0, 2), 1),
        random.randrange(60, 180), 
    ]

    if (bin_positive):
        data.extend([0 for _ in range(arg.binary)])
    else:
        data.extend([random.randrange(2) for _ in range(arg.binary)])

    data.extend([random.randrange(200) for _ in range(arg.irrelevant)])

    return data

def main():
    args = parse_arg()

    dataset = []
    total = CONTINUOUS + args.binary + args.irrelevant

    positive_require = 3000
    while(positive_require > 0 or len(dataset) < 10000):
        data = gen_data(args, bin_positive=(positive_require > 0))
        if rule_match(args, data):
            positive_require = positive_require - 1
            data.append(1)
            dataset.append(data)
        elif len(dataset) < 7000:
            data.append(0)
            dataset.append(data)


    cols = [f"col_{i}" for i in range(total)]
    cols.append("Y")
    df = pd.DataFrame(dataset, columns=cols)
    print(df)
    df.to_csv("./rule.csv", index=False)
    print(3000 - positive_require)


if __name__ == '__main__':
    main()
