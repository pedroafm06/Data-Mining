import argparse
import json
from .schema import SOURCE_DEFAULT


def main():
    parser=argparse.ArgumentParser(description='A2: preparação e transformação reproduzível; rotina anterior preservada como referência histórica')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare',help='Preparação histórica anterior; para a revisão atual use preprocess');p.add_argument('--source',default=str(SOURCE_DEFAULT));p.add_argument('--output',default=None)
    from .schema import PARTITIONS_DEFAULT
    current=sub.add_parser('preprocess',help='Limpeza e transformações atuais da A2, sem treinamento preditivo')
    current.add_argument('--source',type=str,default=str(SOURCE_DEFAULT))
    current.add_argument('--partitions',type=str,default=str(PARTITIONS_DEFAULT))
    current.add_argument('--output-dir',type=str,default=None)
    args=parser.parse_args()
    if args.command=='preprocess':
        from .preprocessing.run import run_preprocessing
        try:run_preprocessing(source=args.source,partitions=args.partitions,output_dir=args.output_dir)
        except (FileNotFoundError,ValueError) as error:parser.error(str(error))
        return
    if args.command=='prepare':
        from .io import write_prepared
        result=write_prepared(args.source,args.output)
        print(json.dumps({'n_source':result.summary['n_source'],'n_treated':result.summary['n_treated'],'n_eligible':result.summary['n_eligible'],'date_statuses':result.summary['date_statuses'],'age_sources':result.summary['age_sources']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
