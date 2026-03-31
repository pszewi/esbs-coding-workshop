import scrape_clean as sc
import analysis 
import logging
import subprocess

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("demo-project/pipeline.log"),
        logging.StreamHandler()        # also prints to console
    ]
)

if __name__=="__main__":

    sc.scrape_clean()
    analysis.run()

    # final step in reproducibility: report your environment setup when finishing the project!
    subprocess.run(
        ["conda", "env", "export"],
        stdout=open("demo-project/environment.yml", "w"),
        check=True
    )
