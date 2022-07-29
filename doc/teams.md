# Teams

Commands related to management of teams are grouped under the `teams` command
prefix. Run the following command to see a list of all available `teams`
commands:

```sh
okdata teams -h
```

Contents:
* [Listing teams](#listing-teams)
* [Editing team details](#editing-team-details)
* [Listing team members](#listing-team-members)

## Listing teams

The following command displays a list of every Origo team along with your
membership status in each of them:

```sh
okdata teams ls
```

Use the `--my` option to list only those teams you're a member of:

```sh
okdata teams ls --my
```

## Editing team details

Use the following command to edit the details of any team you're a member of:

```sh
okdata teams edit
```

The attributes you can edit are the team's:

- Name
- Email address
- Slack channel URL

## Listing team members

The following command lets you pick a team and list its members (even from the
ones you're not a member of):

```sh
okdata teams list-members
```

Use the `--my` option to restrict the selection of teams to those you're a
member of:

```sh
okdata teams list-members --my
```
