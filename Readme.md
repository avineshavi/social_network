To up the frist we need to follow some steps:

Need to check that docker-compose is installed in your local machine if not installed need to install docker-compose steps to install docker and docker compose(ubuntu 20.04)

Step 1: Update Your System
```sudo apt-get update```

Step 2: Install Docker
Install prerequisite packages:
```sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common```

    Add Docker’s official GPG key:
   ```curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - ```

    Add the Docker repository to APT sources:
   ```sudo apt-get update```

    Install Docker CE (Community Edition):
   ```sudo apt-get install -y docker-ce```

    Verify that Docker is installed correctly:
   ```sudo systemctl status docker```

    Add your user to the Docker group (optional):
   ```sudo usermod -aG docker $USER```

Step 3: Install Docker Compose
```sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose```

    Download the current stable release of Docker Compose:
   ```sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*?(?=")')/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose```

    Apply executable permissions to the Docker Compose binary:
   ```sudo chmod +x /usr/local/bin/docker-compose```

    Verify that Docker Compose is installed correctly:
   ```docker-compose --version```

After successfully installation of docker and docker-compose
Now the docker is ready to up run the command in terminal
```docker-compose up --build``` 
only one you need to run this command after that only need to run
```docker-compose up -d```(To up the server)
```docker-compose down```(To down the server)

To check the logs of django container(if you need check other containers log just change the container name here drf_web_1 is the django container name)
```docker logs -f drf_web_1 ```

I have also added a filename called ```registration_users_list.txt``` to register the users(JSON data)

Additionally I have added an extra API to list users
```URL : http://localhost:8000/api/users-list/```
Because need the ids to send/accept/reject

In the URL : ```path('api/friend-requests/send/<int:receiver_id>/', SendFriendRequestView.as_view(), name='send_friend_request'),```
receiver_id equal to id(ID will get from url ``` http://localhost:8000/api/users-list/```)



In the URL : ```path('api/friend-requests/accept/<int:pk>/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),``` pk is the id of FriendRequest table(The id will get from the api url ```http://localhost:8000/api/friend-requests-pending/```)

In the URL : ```path('api/friend-requests/reject/<int:pk>/', RejectFriendRequestView.as_view(), name='reject_friend_request'),``` pk is the id of FriendRequest table(The id will get from the api url ```http://localhost:8000/api/friend-requests-pending/```)

The Postman endpoints are savesd in the filename - social_network.postman_collection.json