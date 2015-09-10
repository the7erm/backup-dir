KISS (Keep it simple) backup script that creates snapshots of the src dir.

- 23 hourly
- 7 daily
- 6 weekly
- 12 monthly
- 5 yearly

# Example usage
```
./backup-dir.py <src> <dst>
```

# Real world usage
```
./backup-dir.py ~/git ~/disk2/backup/
```

Then it creates folder structure that looks like this.
```
~/disk2/backup/git/git.0
~/disk2/backup/git/git.daily.0
~/disk2/backup/git/git.hourly.0
~/disk2/backup/git/git.monthly.0
~/disk2/backup/git/git.weekly.0
~/disk2/backup/git/git.yearly.0
```

### Features
- auto rotates dirs based on their date.
- hardlinks files so you're not wasting a bunch of space.
- uses `rsync`


#### Setting up a cron.
`crontab -e`

```
0 * * * * /path/to/backup/script/backup-dir.py <src> <dst>
# * * * * *  command to execute
# │ │ │ │ │
# │ │ │ │ │
# │ │ │ │ └───── day of week (0 - 6) (0 to 6 are Sunday to Saturday, or use 
# │ │ │ │        names; 7 is Sunday, the same as 0)
# │ │ │ └────────── month (1 - 12)
# │ │ └─────────────── day of month (1 - 31)
# │ └──────────────────── hour (0 - 23)
# └───────────────────────── min (0 - 59)
```
