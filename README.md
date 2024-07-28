## **RC column design use Python**
This CMD app compute and display IR diagram for a column section depend on your trials.
So, you can use it in column design when you have loads on section.
### Instructions

1. Install Python, Git, Anaconda, and VSCode

- [Python](https://www.python.org/downloads/)
- [Git](https://github.com/git-guides/install-git)
- [Anaconda](https://docs.anaconda.com/anaconda/install/index.html)
- [VSCode](https://code.visualstudio.com/download)

2. Go to your project directory

```
cd <your project folder path>
```

3. Clone this repository

```
git clone https://github.com/Suzanoo/column.git
```

4. Create conda env and activate it

```
 conda create --name <your conda env name> python=3.10
 conda activate <your conda env name>
```

5. Install dependency via requirements.txt

```
pip install -r requirements.txt
```

6. Enjoy !!
```
python app/rect.py --b=30 --h=50 --Pu=2500 --Mux=120 --Muy=25
python app/circular.py  --Pu=2500 --Mux=120 --Muy=25

Look at FLAGS definition for alternative
```

Give me comment at: highwaynumber12@gmail.com
