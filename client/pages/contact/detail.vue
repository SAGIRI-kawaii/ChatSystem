<template>
	<view class="">
		<view class="padding bg-white flex solid-bottom no-wrap">
			<view class="margin-top-bottom cu-avatar xl radius margin-left" :style="{backgroundImage:'url(' + friendInfo.avatar + ')'}"></view>
			<view class="margin-top-bottom margin-left flex">
				<view class="margin-left-xs content margin-top-xs">
					<view class="text-xl">
						<text class="text-bold text-black">{{ friendInfo.nickname }}</text>
					</view>
					<view class="text-xs margin-top-xs" style="width: 100%;">
						<text class="uni-lastmsg text-bold text-black">{{ friendInfo.sign }}</text>
					</view>
				</view>
			</view>
		</view>
<!-- 		<view class="bg-white">
			<view class="cu-bar bg-white margin-top-xs">
				<view class="margin-left ">群组成员</view>
			</view>
			<view class="bg-white margin-left margin-right">
				<view class="grid grid-square margin-bottom text-center col-5">
					<view class="bg-img bg-blue" v-for="(item,indexs) in groupMembers" :key="indexs" :style="{backgroundImage:'url(' + (id_to_avatar[item.user_id]) + ')'}"></view>
				</view>
			</view>
		</view> -->
		<view class="padding flex flex-direction">
			<button class="cu-btn bg-white lg" @click="goToChat(friendInfo.user_id)">开始聊天</button>
			<button class="cu-btn bg-red margin-tb-sm lg">删除好友</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				friendInfo: {
					"user_id": 123,
					"avatar": "",
					"nickname": "SAGIRI",
					"sign": "纱雾赛高！"
				}
			}
		},
		onLoad(option) {
			this.getFriendInfo(option.user_id)
			this.goToChat = getApp().globalData.goToChat
		},
		methods: {
			getFriendInfo(user_id) {
				const url = getApp().globalData.apiUrl + "/info/user"
				var that = this;
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"account": getApp().globalData.accountInfo.account,
						"cookie": getApp().globalData.accountInfo.cookie,
						"target": user_id
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						// console.log(result)
						if(result.code == 200){
							result = result.data
							result.avatar = result.avatar != null ? result.avatar : getApp().globalData.defaultAvatar
							result.nickname = result.nickname != null ? result.nickname : result.username
							that.friendInfo = result
						}else if(result.code == 401){
							// 跳转登录
						}else if(result.code == 403){
							
						}else {
							
						}
					} 
				});
			}
		}
	}
</script>

<style>
</style>
