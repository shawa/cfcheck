# CFCheck

Tool to check whether or not a site blocks Tor via CloudFlare.

## Why
Some sites appear to be blocking Tor some of the time, while at other
times, Tor connections go right through.

We can enumerate all of the exits, then for each one launch Tor and exit
through it and attempt to see if the site is either:
    * Behind a CloudFlare CAPTCHA
    * Behind CloudFlare

To avoid hammering the site, there's a default rate limit set to 15s, on top of
how long it takes to launch Tor and build circuits.

## Usage
First get all the exits from https://check.torproject.org/exit-addresses
CFCheck expects a file with a single IP address per line.

You can fetch them and filter them into `exits.txt` with:
```bash
curl 'https://check.torproject.org/exit-addresses' | grep ExitAddress | cut -d ' ' -f 2 > exits.txt
```

CFCheck will print comma-separated values to stdout; the exit IP address and
what it determined is the being-blocked-by-cloudflare status of the site

```
$ python3 cfcheck.py --randomize-ips=True --sample-size=10 example.com exitips.txt
198.58.107.53, other
82.161.206.16, other
213.227.165.50, other
...
```

For the moment, the being-blocked-by-cloudflare status will be one of
* `captcha`, the text 'CAPTCHA' is on the page
* `cloudflare_active`, the text 'CloudFlare' is on the page
* `other` neither of these conditions were met.

**Note how rudimentary these are. Don't depend on the results from this for anything serious just yet.**

Sometimes Tor will fail to build circuits to the specified exit, in which case it will be `tor_timeout`.

## Disclaimer
You're most likely a responsible person, and I hate writing these, but anyway:

### Be Reasonable
This should certainly be a not-first resort, if you notice a site is blocking
Tor, ask them to whitelist exits in their config.
That is, if at any point you hit a CAPTCHA on a site, just reach out to the
site owners and ask; don't immediately go and test every single exit.
Most all of the time site operators are not aware of the problem.

### Anonymity
I'm not making any guarantees regarding anonymity provided by tor when you use
_this_ tool, for one, I'm not vouching that `pycurl` won't inadvertently leak
your real IP address to the site or any other intermediary.

Moreover, I'd be willing to bet CFCheck's traffic patterns are not exactly
indistinguishable from real tor traffic.
