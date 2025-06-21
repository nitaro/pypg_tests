# Python Postgres Tests: Insert or Update

This is small, unruly mess (i.e. I don't care) for testing performance and memory when inserting (creating) or updating records in Postgres with Python. It's on GitHub for shiggles. You probably shouldn't use it. In fact, you should probably [read something else](https://archive.org/details/assassinationofm00weis).

This repo was inspired by circumstances at my current job (~mid 2025) at Fibonacci's Pizza Emporium.

You might know the slogan:

> Get 🍕🍕🍕🍕🍕 for the price of 🍕🍕🍕 ... or 🍕🍕🍕🍕🍕🍕🍕🍕🍕🍕🍕🍕🍕 for the price of 🍕🍕🍕🍕🍕🍕🍕🍕!
>
> Your family will love our Golden Ratio slices!

We use SQLAlchemy a good bit and while I think it makes some things easier to do - like getting things up and running, there are times when I think the long term cost of using it exceeds the benefits - particularly with respect to "insert or update" scenarios where a record has to be created anew if it does not exist or otherwise updated.

There's something to be said about the overhead of researching how to do something in SQLAlchemy when:

1. you already know how to achieve the desired outcome with raw SQL or
1. you need to learn how to achieve something performant in which case the initial research would revolve around raw SQL _followed_ by learning how to implement it in SQLAlchemy.

## Installation

First, you'll need Linux or MacOS. One of the major dependencies, [Memray](https://github.com/bloomberg/memray), doesn't support Windows or other platforms as of June 2025.

You'll also need [Postgres](https://www.postgresql.org/) 15 or greater because I wanted to test the relatively newer [MERGE](https://www.postgresql.org/docs/current/sql-merge.html) statement.

If you have [pipenv](https://pipenv.pypa.io/en/latest/), do:

    pipenv sync --dev

Otherwise, there's a `requirements.txt` file for installing dependencies.

Copy the `.env_dist` file to a new file, `.env`. It should be in the same directory as `Pipfile`.

Create a Postgres database for testing, e.g. `$ createdb my_database`.

Fill in `.env` with the connection values for your Postgres db. _Keep `TOTAL_ITEMS` and `TOTAL_THREADS` set to 5 for now._

### Making a Test Run

Assuming `pipenv`, do:

    $ pipenv shell                  # sources `.env` and enters the virtual env
    $ python -m main                # shows available commands
    $ python -m main describe       # prints Markdown of individual test descriptions
    $ python -m main create_tables  # creates User and Address tables in your db
    $ python -m main count_rows     # should be (0, 0), i.e zero User and Address rows
    $ python -m main test_all       # runs every individual script in `/db_tests` twice: insert then update
                                    # let's call this a "test run" - i.e. we've run the individual tests
    $ python -m main count_rows     # should be (5,5)
    $ python -m main print_rows     # prints representation of row data

Now, inspect the `/results` directory. There should be a set of files with the same prefix - aka the "test run identifier".

Example:

    results/
    ├── 20250505_071455_PM651624.conf
    ├── 20250505_071455_PM651624.csv
    ├── 20250505_071455_PM651624.diff
    ├── 20250505_071455_PM651624.log

### Test Run Files

Here's what each file is about:

1. `conf`: a copy of the environmental variables from `.env`
    - so you know what was used for the test run
1. `csv`: info about the test run with the following columns about each individual test
    - `test`: (str) name of test plus the suffix "-insert" or "-update"
    - `totals`: (int, int) how many respective User and Address rows the test inserted or updated
    - `success`: (bool) if the test resulted in exactly N User rows and N Address rows, where N = the "TOTAL_ITEMS" env var
        - the correctness of the row _values_ are not checked
    - `duration`: (float) how long the test took (seconds)
    - `memory`: (float) how much memory the test used (megabytes) according to Memray
2. `diff`: the current Git commit and the diff (if there is one) between the commit and the actual running code
    - so you know what code was used for the test run
3. `log`: log file of the test run
    - so you can go blind investigating errors

Now run `$ python -m main test_all` again.

There should be another set of test run files a la:

    results/
    ├── 20250505_071455_PM651624.conf  # previous test run
    ├── 20250505_071455_PM651624.csv
    ├── 20250505_071455_PM651624.diff
    ├── 20250505_071455_PM651624.log
    ├── 20250505_071600_PM524461.conf  # new test run
    ├── 20250505_071600_PM524461.csv
    ├── 20250505_071600_PM524461.diff
    └── 20250505_071600_PM524461.log

### Exploring Test Runs

#### Aggregation

Run `$ python -m main aggregate`.

A CSV should print to screen with aggregated data from _all_ test runs - courtesy of [Pandas](https://pandas.pydata.org/).

The dataframe has these columns:

1. `test`: same as previously described ...
1. `average_duration`: exactly what you think it is ...
2. `average_memory`: ☝️ (ditto but memory)
3. `success_rate`:
    - 0 means the test never created all the expected User and Address rows
    - 1 means it always did
    - a value between 0 and 1 means the test creates all expected rows only _some of the time_
5. `z_duration`: test's z-score for duration values
8. `z_memory`: ☝️ (ditto but memory)

#### Correlation

Now run `$ python -m main correlate`.

A CSV should print to screen with correlated data from _all_ test runs - using the [Pearson correlation coefficient](https://www.youtube.com/watch?v=k7IctLRiZmo&pp=0gcJCb4JAYcqIYzv).

#### Visualization

Now run `$ python -m main graph`.

Two [Plotly](https://plotly.com/) bar charts should open in your default browser.

One chart will show average duration times ("performance") per test. The other will show average memory consumption.

My goal is that - between the two graphs - maybe it'll be easier to see which approach to inserting or updating records in Postgres are good choices for Python, which ones are bad, or which ones are suspiciously erroneous (i.e. I messed something up).

... and which ones are such a pain to research in SQLAlchemy that reverting to raw SQL might be the better option. By the way, that's why I avoided an ORM Postgres [Upsert](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html#insert-on-conflict-upsert). I skimmed the documentation and thought "f... it".

##### Wait! ... What's this? A third chart?

> We wouldn't be a good pizzeria without offloading excess product onto the customer while pretending we did it for them.

Yes, there's a third chart - a scatter plot with "z_duration" as the X axis and "z_memory" as the Y.

_Anchovies are underrated._

## How This Works

Each Python script ("test") in `/db_tests` must have a "main" function that accepts a single integer as a parameter, i.e.: `main(total:int) ...`.

Each test is expected to be able to insert or update a `User` and `Address` row for every integer in the range of 0 until the value of `$total`. The `User` and `Address` models/schema are defined in `lib/models.py`.

If the test script is going to execute with threads, it needs to be using the same of number of threads as `lib.config.CONFIG.TOTAL_THREADS`.

All this allows this "framework" to run each script as an independent test and measure its performance and memory.

Each test will be executed twice. The first time will be with empty tables - i.e. inserts. After the inserts complete, the script is executed again - i.e. updates.

For a simple example, see `db_tests/sa_static_session.py`.

### Adding/Removing Tests

To add another test, just add another Python script in `/db_tests`. To remove a test, just delete the file or rename it to have an extension other than `.py`.

### Removing Test Run Results

If you want to execute a new set of test runs, say with a higher value for `TOTAL_ITEMS` then change `TOTAL_ITEMS` in `.env`, do `$ source .env` and `$ rm -fr /results` _before_ running `$ python -m main test_all`.

The code doesn't aggregate normalized test run data, so it can't help you if some of your files in `/results` were based on a `TOTAL_ITEMS` value of 10 and others were done with a value of 100. So, you probably need to remove all previous data before you change values for `TOTAL_ITEMS` or `TOTAL_THREADS`.

The possible exception to this is the scatter plot which uses z-scores for duration and memory. So you might be able to intermix test runs with varied values for `TOTAL_ITEMS` or `TOTAL_THREADS` and still view the scatter plot to get a sense of what tests are "best" - i.e. those closest to the bottom left.

## How I'm Using This

After having created some test scripts in `/db_tests` that cover a few different insert or update techniques - with and without threading, I'll do something like this:

    # start the virtual env and auto-source `.env`
    $ pipenv shell

    # wipe any existing data
    $ rm -fr results

    # make a few test runs
    $ seq 3 | xargs -I {} python -m main test_all

    # graph the data, look at it
    $ python -m main graph

    # peruse the aggregated data in a spreadsheet
    $ python -m aggregate > agg.csv
    $ open agg.csv

    # peruse the correlated data in a spreadsheet
    $ python -m correlate > cor.csv
    $ open cor.csv

Example graphs are in ... `/example_graphs`.

## Findings and a Rant

I'm consistently getting superior performance when using raw SQL statements especially with threading and especially with using a custom class to queue multiple statements in a simple, thread-safe manner that commits once the queue reaches a certain size - see `lib.commit_queue.SACommitQueue`. There also appears to be a positive correlation between performance and memory.

Overall, I just feel better using raw SQL because it's easier for me to _understand_ what's actually going on. In other words, there's an implicit metric lurking underneath - a sort of "comprehensibility score".

Take a look at this comment from `db_tests/sa_static_session_merge.py`:

> I'm probably doing something wrong, but this is exactly the point - I'm futzing around with the ORM instead of getting work done.
> Just read all the merge caveats here: https://docs.sqlalchemy.org/en/20/orm/session_state_management.html#merge-tips and ask yourself if this is what you want to deal with?

~~I'm sure a lot of the pure SQLAlchemy tests I tried that use threading have some fatal flaw, but with a larger `TOTAL_ITEMS` value - say 1000 - I'm seeing that SQLAlchemy seems to drop rows. In other words, I might only see 998 total User and Address rows when I should see 1000.~~ **Correction**: _this appears to just have been my fault, plain and simple. I'm not seeing such errors anymore. I still think everything below (written while these errors were still occurring) still holds up as it took more effort than I'd have liked to fix the errors, plus the larger points below are about abstraction and architecture._

The pedantic response is that this is likely User-error, SQLAlchemy is not to blame, my findings are erroneous, and I need to prostrate myself before the SQLAlchemy source code, etc.

Fair enough. But I'd argue that a more nuanced interpretation is in order.

While a flawed test may in fact demonstrate my ignorance of SQLAlchemy, maybe it also demonstrates the bigger problem that the "long term cost of using" SQLAlchemy (or another ORM) "exceeds the benefits".

I'm no SQL expert and - sure - there are are differences between say a MySQL vs. a Postgres that an ORM could abstract away - allowing one to switch databases "under the hood" - but I think there are two problems with this.

One, if the ORM promises abstraction, then why are database-specific dialects needed? The abstraction seems incomplete. Plus, SQL _itself_ is an abstraction.

Second, the better way to abstract away database diversity would seem to be via simple architecture choices.

In other words, maybe I should I discipline myself to _avoid_ importing SQLAlchemy at will throughout my code-base whenever I need to touch a database. Maybe I should just limit which module/s I allow to interact with a database e.g.:

    # order_pizza.py  # Who doesn't like a good pizza py?
    from db_functions import create_or_update_user, dispatch_driver, find_driver

    def process_delivery_order(order, ...):

        user = create_or_update_user(...)
        dispatch_driver(driver=find_driver(user.address),
                        destination=user.address
                        delivery_items=order.items)

        return

The point here is that `order_pizza.py` _could_ make direct SQLAlchemy calls to the database ... but should it? If we're so worried about abstracting away problems, why would we allow ourselves to do that? If we want to switch from Postgres to MySQL and had thought more about architecture and organization, then we'd only need to change functions in `db_functions.py`. That's to say we can achieve abstraction through an arguably cleaner and more disciplined _architecture_ - irrespective of whether or not an ORM is in use, in part or in full.

And for all we know, `db_functions` already handles multiple databases as it sees fit:

    # db_functions.py
    def create_or_update_user(...):
        if GLOBAL_DB_DIALECT == "postgres":
            ...
        else:
            ...

If I'm `order_pizza.py` why should I know anything about SQLAlchemy, or even what SQL is needed? Why should I even know if we're even using a database at all?

Sorry, but in terms of using an ORM, I just don't buy a large part of what I think the sell is.

ORMs are just tools. They don't confer architecture.

## Future Work

I'm not sure I'll touch this repository again, but if I do I'll focus more on making a generic, easy-to-use "all in one" performance and memory evaluator.

## Helpful Links

- [SQLAlchemy: Streamlining Data Operations with Session.merge() and Beyond](https://iifx.dev/en/articles/5214105#google_vignette)
- [Why standard deviation is important in performance tests](https://medium.com/@gpiechnik/why-standard-deviation-is-important-in-performance-tests-a32e6b77f7a3)
 - [Exactly why ORMs are a bad idea. I've always wondered whether ORMs help or harm](https://news.ycombinator.com/item?id=15435198)
 - [Pepperoni Might be the Safer Topping](https://en.wikipedia.org/wiki/Domoic_acid#Toxicology)
 - [Weiss is Nice, but Bach is Best](https://archive.org/details/shaffer-amadeus-2006-red-by-abraham)
    - I didn't come up with that line.
    - When AI gets this joke, we'll have reached the singularity. And not before.
