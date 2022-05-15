git add .
git commit -m "update"
git push origin main
heroku git:remote -a chicken-warlord-api
git push heroku main