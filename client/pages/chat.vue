<template>
	<view>
		<view class="cu-chat" id="chat-box">
			<!-- <view class="cu-info">
				<text class="cuIcon-roundclosefill text-red "></text> 对方拒绝了你的消息
			</view>
			<view class="cu-info">
				对方开启了好友验证，你还不是他(她)的好友。请先发送好友验证请求，对方验证通过后，才能聊天。
				<text class="text-blue">发送好友验证</text>
			</view> -->
			<view class="cu-item" v-for="(item,index) in messageList" :key="index" :class="item.sender == selfAccount?'self':''">
				<view class="cu-avatar radius" :style="{backgroundImage:'url(' + getAvatar(item.sender) + ')'}" v-show="item.sender != selfAccount"></view>
				<view class="main">
					<view class="content shadow flex-wrap justify-start">
						<view v-html="messageElementToHtml(item.message)"></view>
						<!-- <text>	喵喵喵！喵喵喵！</text><image src="https://ossweb-img.qq.com/images/lol/web201310/skin/big10006.jpg" class="radius" mode="widthFix"></image> -->
					</view>
				</view>
				<view class="cu-avatar radius" :style="{backgroundImage:'url(' + selfAvatar() + ')'}" v-show="item.sender == selfAccount"></view>
				<view class="date">{{ item.time }}</view>
			</view>
		</view>

		<view class="cu-bar foot input" :style="[{bottom:InputBottom+'px'}]">
			<view class="action">
				<text class="cuIcon-roundadd text-grey"></text>
			</view>
			<input class="solid-bottom" :adjust-position="false" :focus="false" maxlength="300" cursor-spacing="10" v-model="messageText"
			 @focus="InputFocus" @blur="InputBlur"></input>
			<button class="cu-btn bg-green shadow" @click="sendMessage">发送</button>
		</view>

	</view>
</template>

<script>
	export default {
		data() {
			return {
				InputBottom: 0,
				isFriend: true,
				messageList: [],
				selfAccount: 0,
				id_to_avatar: {},
				id: 0,
				type: "None",
				messageToSend: [],
				messageText: "",
				wh: 0
			};
		},
		onLoad(option) {
			this.id = option.id
			this.getType(option.id)
			this.getMessages(option.id)
			this.selfAccount = getApp().globalData.accountInfo.account
			this.$nextTick(() => {
			 
				// document.getElementById("scrolldIV2").scrollIntoView();	 //h5端定位到指定位置	
 
				setTimeout(() => {
					uni.createSelectorQuery().select(".cu-chat").boundingClientRect(function(res) { //定位到你要的class的位置
						// console.log("标签获取====>", res)
						uni.pageScrollTo({
							scrollTop: res.height,
							duration: 0
						});
					}).exec()
 
				}, 50)
			})
		},
		onShow() {
			this.getMessages(this.id)
		},
		onHide() {
			// window.clearInterval(this.messagetimer)
		},
		updated() {
			uni.pageScrollTo({
				scrollTop: 99999,
				duration: 300
			})
		},
		methods: {
			handleScroll(e) {
				let scrolltop = e.target.scrollTop;
				scrolltop > 30 ? (this.gotop = true) : (this.gotop = false);
			},
			goBottom() {
				uni.pageScrollTo({
					scrollTop: 99999,
					duration: 300
				})
			},
			InputFocus(e) {
				this.InputBottom = e.detail.height
			},
			InputBlur(e) {
				this.InputBottom = 0
			},
			getMessages(id) {
				if (id in getApp().globalData.chatData){
					this.messageList = getApp().globalData.chatData[id].data
					// console.log(this.messageList)
				}
				this.goBottom();
				// for (var i=0;i<this.messageList.length;i++) {
				// 	this.getAvatar(this.messageList[i].sender + "")
				// 	// console.log(this.messageList[i].sender + "", typeof(this.messageList[i].sender))
				// }
			},
			messageDisplay(message) {
				var display = "";
				for (var i = 0; i < message.message.length; i ++) {
					display += message.message[i].display;
				}
				return display;
			},
			messageElementToHtml(message) {
				var result = ""
				// console.log(message)
				for (var i=0;i<message.length;i++) {
					// console.log(message[i])
					if (message[i] == null) continue;
					if (message[i].type == "Plain") {
						result += "<text>" + message[i].content.replace(/\n/g, "<br/>") + "</text>";
					} else if (message[i].type == "Image") {
						// console.log("<image src='" + message[i].content + "' class='radius' mode='widthFix'></image>")
						result += "<image src='" + message[i].content + "' class='radius' style='display: inline-block; width: 100%; max-width: 100%; height: auto;'></image>";
					}
				}
				// console.log(result)
				return result;
			},
			getType(id) {
				// id = parseInt(id)
				const url = getApp().globalData.apiUrl + "/info/idType/"
				var that = this
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"id": id
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						if (result.code == 200){
							that.type = result.data
						} else {
							that.type = null
						}
					} 
				})
			},
			getCurrentTime() {
				const date = new Date();
				let yy = date.getFullYear();
				let mm = date.getMonth() + 1;
				let dd = date.getDate();
				let hh = date.getHours();
				let mf = date.getMinutes()<10 ? '0' + date.getMinutes() : date.getMinutes();
				let ss = date.getSeconds()<10 ? '0' + date.getSeconds() : date.getSeconds();
				return yy+'/'+mm+'/'+dd+' '+hh+':'+mf+':'+ss;
			},
			sendMessage() {
				if (this.messageToSend == [] || this.messageText == "") {
					return
				}
				getApp().globalData.websocketsend(JSON.stringify({
					"type": "Send" + this.type + "Message",
					"account": getApp().globalData.accountInfo.account,
					"cookie": getApp().globalData.accountInfo.cookie,
					"target": this.id,
					"messageChain": [{
						"type": "Plain",
						"content": this.messageText,
						"display": this.messageText
					}]
				}))
				if (!(this.id in getApp().globalData.chatData)) {
					getApp().globalData.chatData[this.id] = {
						"type": this.type,
						"data": []
					}
				}
				// console.log(JSON.stringify(getApp().globalData.chatData[this.id]))
				getApp().globalData.chatData[this.id].data.push({
					"sender": getApp().globalData.accountInfo.account,
					"time": this.getCurrentTime(),
					"message": [{
						"type": "Plain",
						"content": this.messageText,
						"display": this.messageText
					}]
				})
				this.messageToSend = [];
				this.messageText = "";
			},
			refreshAvatars() {
				for (var i=0;i<this.messageList.length;i++) {
					this.getAvatar(this.messageList[i].sender + "")
					// console.log(this.messageList[i].sender + "", typeof(this.messageList[i].sender))
				}
			},
			getAvatar(id) {
				// console.log(id)
				if (id in this.id_to_avatar && this.id_to_avatar[id] != undefined) {
					return this.id_to_avatar[id]
				} else if (id in getApp().globalData.groupData) {
					this.id_to_avatar[id] = getApp().globalData.groupData[id].avatar
					return this.id_to_avatar[id]
				} else if (id in getApp().globalData.userData) {
					this.id_to_avatar[id] = getApp().globalData.userData[id].avatar
					return this.id_to_avatar[id]
				} else {
					this.id_to_avatar[id] = null
					const url = getApp().globalData.apiUrl + "/info/user/"
					var that = this;
					uni.request({
						url: url,
						method: 'GET',
						data: {
							"account": getApp().globalData.accountInfo.account,
							"cookie": getApp().globalData.accountInfo.cookie,
							"target": id
						},
						dataType:'json'
					}).then(data => {
						var [error, res] = data;
						var result = res.data.data
						that.id_to_avatar[id] = result.avatar
						return result.avatar
					})
				}
			},
			selfAvatar() {
				return getApp().globalData.accountInfo.avatar
			}
		}
	}
</script>

<style>
page{
  padding-bottom: 100upx;
}
</style>
