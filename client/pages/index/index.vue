<template>
	<view>
		<view class="cu-list menu-avatar">
			<view class="cu-item" v-for="(item,index) in messageList" :key="index" @click="goToChat(item.target)">
				<view class="cu-avatar round lg" :style="{backgroundImage:'url(' + id_to_avatar[item.target] + ')'}"></view>
				<view class="chat-content">
					<view class="text-grey">{{ item.displayName }}</view>
					<view class="text-gray text-sm flex">
						<text class="uni-lastmsg">{{ item.display.replace(/\n/g,"") }}</text>
					</view>
				</view>	
				<view class="action">
					<view class="text-grey text-xs">{{ item.timeStr }}</view>
					<view class="cu-tag round bg-grey sm" v-show="item.newMessages?true:false">{{ item.newMessages }}</view>
				</view>
				<view class="move">
					<view class="bg-red">删除</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				modalName: null,
				listTouchStart: 0,
				listTouchDirection: null,
				chatData: {},
				newMessage: {},
				messageList: [],
				id_to_name: {},
				id_to_avatar: {}
			}
		},
		onLoad() {
			this.goToChat = getApp().globalData.goToChat
			this.getChatData()
			this.getNewMessage()
			this.setMessageList()
			this.messagetimer = window.setInterval(() => {
				setTimeout(() => {
					this.getChatData()
					this.getNewMessage()
					this.setMessageList()
					}, 0)
				}, 1000)
		},
		mounted() {
		},
		methods: {
			getChatData() {
				this.chatData = getApp().globalData.chatData
			},
			
			getNewMessage() {
				this.newMessage = getApp().globalData.newMessage
			},
			
			messageDisplay(message, type) {
				var display = "";
				// console.log(message)
				for (var i = 0; i < message.message.length; i ++) {
					display += message.message[i].display;
				}
				return type=="friend"?display:message.sender+': '+display;
			},
			
			timeTransform(time) {
				let weeks = ['日', '一', '二', '三', '四', '五', '六']
				var date = new Date();
				var messageDate = Date.parse(time);
				var week = date.getDay();
				if (week == 0) week = 7;
				var seperator = "-";
				var year = date.getFullYear();
				var month = date.getMonth() + 1;
				var strDate = date.getDate();
				var messageDateStr = time.split(" ")[0]
				var messageYear = messageDateStr.split('-')[0]
				var messageMonth = messageDateStr.split('-')[1]
				var messageDay = messageDateStr.split('-')[2]
				if (month >= 1 && month <= 9) {
					month = "0" + month;
				}
				if (strDate >= 0 && strDate <= 9) {
					strDate = "0" + strDate;
				}
				var currentdate = year + seperator + month + seperator + strDate;
				if (messageDateStr == currentdate) return time.split(" ")[1].split(":").slice(0, 2).join(":");
				if (messageYear < year) return messageYear.slice(2) + '/' + messageMonth + '/' + messageDay;
				var daysDiffrent = Math.floor(Math.abs(date - messageDate) / (24 * 3600 * 1000)) + 1
				if (daysDiffrent == 1) return "昨天";
				if (daysDiffrent == 2) return "前天";
				if (daysDiffrent < 7) return "星期" + weeks[(week + 7 - daysDiffrent) % 7]
				return time.split(" ")[0]
			},
			
			setMessageList() {
				this.messageList = []
				for (var key in this.chatData) {
					if (this.chatData[key].data.length > 0) {
						var lastMessage = this.chatData[key].data.slice(-1)[0];
						this.getInfoFromId(key, this.chatData[key].type)
						this.messageList.push({
							"target": key,
							"time": lastMessage.time,
							"timeStr": this.timeTransform(lastMessage.time),
							"sender": lastMessage.sender,
							"displayName": this.id_to_name[key],
							"display": this.messageDisplay(lastMessage, this.chatData[key].type),
							"newMessages": (key in this.newMessage)?this.newMessage[key]:0
						})
					}
				}
				this.messageList.sort(function(a, b) {
					return b.time < a.time ? -1 : 1
				})
			},
			
			getInfoFromId(id, type) {
				if (type == "friend") {
					if (id in getApp().globalData.userData) {
						this.id_to_name[id] = getApp().globalData.userData[id].nickname != undefined ? getApp().globalData.userData[id].nickname : getApp().globalData.userData[id].username
						this.id_to_avatar[id] = getApp().globalData.userData[id].avatar != null ? getApp().globalData.userData[id].avatar : getApp().globalData.defaultAvatar
					}	
				} else if (type == "friend") {
					if (id in getApp().globalData.groupData) {
						this.id_to_name[id] = getApp().globalData.groupData[id].name != undefined ? getApp().globalData.groupData[id].name : getApp().globalData.groupData[id].group_id
						this.id_to_avatar[id] = getApp().globalData.groupData[id].avatar != null ? getApp().globalData.groupData[id].avatar : getApp().globalData.defaultAvatar
					}	
				}
				const url = getApp().globalData.apiUrl + "/info/" + (type == "friend" ? "user" : "group") + "/"
				var nameResult = "Null";
				var that = this;
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"account": getApp().globalData.accountInfo.account,
						"cookie": getApp().globalData.accountInfo.cookie,
						"target": id
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						// console.log(result)
						if(result.code == 200){
							if (type == "friend") that.id_to_name[id] = result.data.nickname != undefined ? result.data.nickname : result.data.username
							else that.id_to_name[id] = result.data.name != undefined ? result.data.name : result.data.group_id
							that.id_to_avatar[id] = result.data.avatar != null ? result.data.avatar : getApp().globalData.defaultAvatar
							// console.log(that.id_to_avatar[id])
							return;
						}else if(result.code == 401){
							// 跳转登录
						}else if(result.code == 403){
							that.id_to_name[id] = "idNotFoundError";
							that.id_to_avatar[id] = getApp().globalData.defaultAvatar;
						}else {
							that.id_to_name[id] = "displayNameError";
							that.id_to_avatar[id] = getApp().globalData.defaultAvatar;
						}
					} 
				}); 
				return nameResult;
			},
			
			ListTouchStart(e) {
				this.listTouchStart = e.touches[0].pageX
			},
			
			// ListTouch计算方向
			ListTouchMove(e) {
				this.listTouchDirection = e.touches[0].pageX - this.listTouchStart > 0 ? 'right' : 'left'
			},
			
			// ListTouch计算滚动
			ListTouchEnd(e) {
				if (this.listTouchDirection == 'left') {
					this.modalName = e.currentTarget.dataset.target
				} else {
					this.modalName = null
				}
				this.listTouchDirection = null
			}
		},
		destroyed() {
			window.clearInterval(this.messagetimer)
			window.clearInterval(this.infotimer)
		}
	}
</script>

<style>
	.content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.logo {
		height: 200rpx;
		width: 200rpx;
		margin-top: 200rpx;
		margin-left: auto;
		margin-right: auto;
		margin-bottom: 50rpx;
	}

	.text-area {
		display: flex;
		justify-content: center;
	}

	.title {
		font-size: 36rpx;
		color: #8f8f94;
	}
	
	.page {
		height: 100Vh;
		width: 100vw;
	}

	.page.show {
		overflow: hidden;
	}

	.switch-sex::after {
		content: "\e716";
	}

	.switch-sex::before {
		content: "\e7a9";
	}

	.switch-music::after {
		content: "\e66a";
	}

	.switch-music::before {
		content: "\e6db";
	}
	
	.chat-content {		
		position: absolute;
		left: 146upx;
		width: calc(100% - 96upx - 60upx - 120upx - 20upx);
		line-height: 1.6em;
	}
	
	.uni-lastmsg {
		text-overflow: ellipsis;
		overflow: hidden;
		white-space: nowrap;
	}
</style>
