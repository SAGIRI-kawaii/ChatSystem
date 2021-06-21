<script>
	export default {
		globalData: {
			apiUrl: "http://127.0.0.1:12345",
			accountInfo: {
				// account: 10000001,
				// cookie: "testCookie",
				// avatar: ""
				account: 0,
				cookie: "",
				avatar: ""
			},
			websock: null,
			defaultAvatar: "../../static/logo.png",
			chatData: {
				// 100001: {
				// 	"type": "group",
				// 	"data": [
				// 		{
				// 			"sender": 10000001,
				// 			"time": "2021-04-23 11:02:27",
				// 			"message": [
				// 				{
				// 					"type": "Plain",
				// 					"content": "草",
				// 					"display": "草"
				// 				},
				// 				{
				// 					"type": "Image",
				// 					"content": "https://ossweb-img.qq.com/images/lol/web201310/skin/big10006.jpg",
				// 					"display": "[图片]"
				// 				}
				// 			]
				// 		},
				// 	]
				// },
			},
			userData: {
				10000001: {
					"nickname": "nickname",
					"sign": "啥也没有",
					"avatar": "url"
				}
			},
			groupData: {
				100001: {
					"name": "name",
					"description": "啥也没有",
					"avatar": "url"
				}
			},
			newMessage: {
				10000000: 7,
				100001: 10,
				100002: 0
			},
			goToChat(id) {
				uni.navigateTo({
					url: "/pages/chat?id=" + id
				})
			},
			websocketsend(Data) {
				getApp().globalData.websock.send(Data);
			},
			timeFormat(time) {
				let date = new Date(time)
				let yy = date.getFullYear();
				let mm = date.getMonth() + 1;
				let dd = date.getDate();
				let hh = date.getHours();
				let mf = date.getMinutes()<10 ? '0' + date.getMinutes() : date.getMinutes();
				let ss = date.getSeconds()<10 ? '0' + date.getSeconds() : date.getSeconds();
				return yy+'/'+mm+'/'+dd+' '+hh+':'+mf+':'+ss;
			},
			getChatData() {
				const url = getApp().globalData.apiUrl + "/info/chatData/"
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"account": getApp().globalData.accountInfo.account,
						"cookie": getApp().globalData.accountInfo.cookie
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						console.log(result)
						if(result.code == 200){
							result = result.data
							var friend = result.friend
							var group = result.group
							var friendLength = 0
							var groupLength = 0
							for(var i in friend) friendLength++;
							for(var i in group) groupLength++;
							for (var i=0;i<friendLength;i++) {
								var friendId = (friend[i].sender != getApp().globalData.accountInfo.account?friend[i].sender:friend[i].recevier)
								// console.log(friend[i], friendId)
								if (friendId in getApp().globalData.chatData) {
									getApp().globalData.chatData[friendId].data.push({
										"sender": friend[i].sender,
										"time": getApp().globalData.timeFormat(friend[i].time),
										"message": friend[i].messageChain
									})
								} else {
									getApp().globalData.chatData[friendId] = {
										"type": "friend",
										"data": [{
											"sender": friend[i].sender,
											"time": getApp().globalData.timeFormat(friend[i].time),
											"message": friend[i].messageChain
										}],
									}
								}
							}
							for (var i=0;i<groupLength;i++) {
								if (group[i].group_id in getApp().globalData.chatData) {
									getApp().globalData.chatData[group[i].group_id].data.push({
										"sender": group[i].sender,
										"time": getApp().globalData.timeFormat(group[i].time),
										"message": group[i].messageChain
									})
								} else {
									getApp().globalData.chatData[group[i].group_id] = {
										"type": "group",
										"data": [{
											"sender": group[i].sender,
											"time": getApp().globalData.timeFormat(group[i].time),
											"message": group[i].messageChain
										}],
									}
								}
							}
							console.log(getApp().globalData.chatData)
						}else if(result.code == 401){
							// 跳转登录
						}else {
							
						}
					} 
				});
			},
			getGroups() {
				const url = getApp().globalData.apiUrl + "/info/getJoinedGroups/";
				var that = this;
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"account": getApp().globalData.accountInfo.account,
						"cookie": getApp().globalData.accountInfo.cookie
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						if(result.code == 200){
							result = result.data
							var data = {}
							for (var i=0;i<result.length;i++) {
								if (result[i].avatar == null) result[i].avatar = getApp().globalData.defaultAvatar
								data[result[i].group_id] = result[i]
							}
							getApp().globalData.groupData = data
						}else if(result.code == 401){
							// 跳转登录
						}else if(result.code == 403){
							
						}else {
							
						}
					}
				});
			},
			getFriends() {
				const url = getApp().globalData.apiUrl + "/info/getFriends/";
				// console.log(url)
				var that = this;
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"account": getApp().globalData.accountInfo.account,
						"cookie": getApp().globalData.accountInfo.cookie
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						if(result.code == 200){
							result = result.data
							var data = {}
							for (var i=0;i<result.length;i++) {
								if (result[i].avatar == null) result[i].avatar = getApp().globalData.defaultAvatar
								data[result[i].user_id] = result[i]
							}
							getApp().globalData.userData = data
						}else if(result.code == 401){
							// 跳转登录
						}else if(result.code == 403){
							
						}else {
							
						}
					}
				});
			},
			initWebSocket() { //初始化weosocket
				const wsuri = "ws://127.0.0.1:12346";
				getApp().globalData.websock = new WebSocket(wsuri);
				getApp().globalData.websock.onmessage = getApp().globalData.websocketonmessage;
				getApp().globalData.websock.onopen = getApp().globalData.websocketonopen;
				getApp().globalData.websock.onerror = getApp().globalData.websocketonerror;
				getApp().globalData.websock.onclose = getApp().globalData.websocketclose;
			},
			websocketonopen() { //连接建立之后执行send方法发送数据
				console.log('WebSocket连接成功')
				getApp().globalData.websocketsend(JSON.stringify({
					"type": "Hello",
					"account": getApp().globalData.accountInfo.account,
					"cookie": getApp().globalData.accountInfo.cookie,
				}))
			},
			websocketonerror() {//连接建立失败重连
				getApp().globalData.initWebSocket();
			},
			websocketonmessage(e) { //数据接收
				var data = e.data
				console.log(data)
				try {
					data = JSON.parse(data)
				} catch(error) {
					
				}
				// console.log(data)
				if ("type" in data) {
					if (data.type == "group") {
						var group_id = parseInt(data.group.group_id)
						if (!group_id in getApp().globalData.chatData) {
							getApp().globalData.chatData[group_id] = {
								"type": "group",
								"data": []
							}
						}
						console.log(group_id)
						getApp().globalData.chatData[group_id].data.push({
							"sender": data.sender.user_id,
							"time": data.time,
							"message": data.messageChain
						})
						getApp().globalData.newMessage[group_id]++;
					} else if (data.type == "friend") {
						var friend_id = parseInt(data.sender.user_id)
						if (!friend_id in getApp().globalData.chatData) {
							getApp().globalData.chatData[friend_id] = {
								"type": "friend",
								"data": []
							}
						}
						console.log(data.messageChain)
						getApp().globalData.chatData[friend_id].data.push({
							"sender": data.sender.user_id,
							"time": data.time,
							"message": data.messageChain
						})
						// console.log(getApp().globalData.chatData[friend_id].data)
						getApp().globalData.newMessage[friend_id]++;
					}
				}
			},
			websocketclose(e) {  //关闭
				console.log('断开连接', e);
			},
		},
		onLaunch: function() {
			console.log('App Launch')
			this.cookieCheck();
			getApp().globalData.getFriends();
			getApp().globalData.getGroups();
			this.getChatData();
		},
		onShow: function() {
			
		},
		onHide: function() {
			
		},
		created(){
			
		},
		destroyed() {
            this.websocketclose()
		},
		methods: {
			websocketonopen() { //连接建立之后执行send方法发送数据
				console.log('WebSocket连接成功')
				getApp().globalData.websocketsend(JSON.stringify({
					"type": "Hello",
					"account": getApp().globalData.accountInfo.account,
					"cookie": getApp().globalData.accountInfo.cookie,
				}))
			},
			websocketonerror() {//连接建立失败重连
				getApp().globalData.initWebSocket();
			},
			websocketonmessage(e) { //数据接收
				var data = e.data
				console.log(data)
				try {
					data = JSON.parse(data)
				} catch(error) {
					
				}
				// console.log(data)
				if ("type" in data) {
					if (data.type == "group") {
						var group_id = parseInt(data.group.group_id)
						if (!group_id in getApp().globalData.chatData) {
							getApp().globalData.chatData[group_id] = {
								"type": "group",
								"data": []
							}
						}
						console.log(group_id)
						getApp().globalData.chatData[group_id].data.push({
							"sender": data.sender.user_id,
							"time": data.time,
							"message": data.messageChain
						})
						getApp().globalData.newMessage[group_id]++;
					} else if (data.type == "friend") {
						var friend_id = parseInt(data.sender.user_id)
						if (!friend_id in getApp().globalData.chatData) {
							getApp().globalData.chatData[friend_id] = {
								"type": "friend",
								"data": []
							}
						}
						console.log(data.messageChain)
						getApp().globalData.chatData[friend_id].data.push({
							"sender": data.sender.user_id,
							"time": data.time,
							"message": data.messageChain
						})
						// console.log(getApp().globalData.chatData[friend_id].data)
						getApp().globalData.newMessage[friend_id]++;
					}
				}
			},
			websocketsend(Data) {//数据发送
				getApp().globalData.websock.send(Data);
			},
			websocketclose(e) {  //关闭
				console.log('断开连接', e);
			},
			getChatData() {
				const url = getApp().globalData.apiUrl + "/info/chatData/"
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"account": getApp().globalData.accountInfo.account,
						"cookie": getApp().globalData.accountInfo.cookie
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						console.log(result)
						if(result.code == 200){
							result = result.data
							var friend = result.friend
							var group = result.group
							var friendLength = 0
							var groupLength = 0
							for(var i in friend) friendLength++;
							for(var i in group) groupLength++;
							for (var i=0;i<friendLength;i++) {
								var friendId = (friend[i].sender != getApp().globalData.accountInfo.account?friend[i].sender:friend[i].recevier)
								// console.log(friend[i], friendId)
								if (friendId in getApp().globalData.chatData) {
									getApp().globalData.chatData[friendId].data.push({
										"sender": friend[i].sender,
										"time": friend[i].time,
										"message": friend[i].messageChain
									})
								} else {
									getApp().globalData.chatData[friendId] = {
										"type": "friend",
										"data": [{
											"sender": friend[i].sender,
											"time": friend[i].time,
											"message": friend[i].messageChain
										}],
									}
								}
							}
							for (var i=0;i<groupLength;i++) {
								if (group[i].group_id in getApp().globalData.chatData) {
									getApp().globalData.chatData[group[i].group_id].data.push({
										"sender": group[i].sender,
										"time": group[i].time,
										"message": group[i].messageChain
									})
								} else {
									getApp().globalData.chatData[group[i].group_id] = {
										"type": "group",
										"data": [{
											"sender": group[i].sender,
											"time": group[i].time,
											"message": group[i].messageChain
										}],
									}
								}
							}
							console.log(getApp().globalData.chatData)
						}else if(result.code == 401){
							// 跳转登录
						}else {
							
						}
					} 
				});
			},
			cookieCheck() {
				const url = getApp().globalData.apiUrl + "/user/cookieCheck"
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"account": getApp().globalData.accountInfo.account,
						"cookie": getApp().globalData.accountInfo.cookie
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						console.log(result)
						if (result.data == true) {
							getApp().globalData.initWebSocket();
						} else {
							uni.showToast({
								title: "您尚未登录，即将跳转至登录页面...",
								icon: "none"
							})
							setTimeout(function() {
								uni.navigateTo({
									url: "/pages/login-register"
								})
							}, 1500);
						}
					} 
				}); 
			},
		}
	}
</script>

<style>
	@import url("/colorui/animation.css");
	@import url("/colorui/icon.css");
	@import url("/colorui/main.css");
</style>
