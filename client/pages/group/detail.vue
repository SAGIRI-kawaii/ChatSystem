<template>
	<view class="">
		<view class="padding bg-white flex solid-bottom no-wrap">
			<view class="margin-top-bottom cu-avatar xl radius margin-left" :style="{backgroundImage:'url(' + groupInfo.avatar + ')'}"></view>
			<view class="margin-top-bottom margin-left flex">
				<view class="margin-left-xs content margin-top-xs">
					<view class="text-xl">
						<text class="text-bold text-black">{{ groupInfo.name }}</text>
					</view>
					<view class="text-xs margin-top-xs" style="width: 100%;">
						<text class="uni-lastmsg text-bold text-black">{{ groupInfo.description }}</text>
					</view>
				</view>
			</view>
		</view>
		<view class="bg-white">
			<view class="cu-bar bg-white margin-top-xs">
				<view class="margin-left ">群组成员</view>
			</view>
			<view class="bg-white margin-left margin-right">
				<view class="grid grid-square margin-bottom text-center col-5">
					<view class="bg-img bg-blue" v-for="(item,indexs) in groupMembers" :key="indexs" :style="{backgroundImage:'url(' + (id_to_avatar[item.user_id]) + ')'}"></view>
				</view>
			</view>
		</view>
		<view class="padding flex flex-direction">
			<button class="cu-btn bg-white lg" @click="goToChat(groupInfo.group_id)">开始聊天</button>
			<button class="cu-btn bg-red margin-tb-sm lg">退出群组</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				groupInfo: {
					"group_id": 123,
					"avatar": "",
					"name": "Iron Man",
					"description": "一个钢铁侠爱好者聚集地"
				},
				groupMembers: [],
				id_to_avatar: {}
			}
		},
		onLoad(option) {
			this.goToChat = getApp().globalData.goToChat
			this.getGroupInfo(option.group_id)
			this.getGroupMember(option.group_id)
		},
		methods: {
			getGroupInfo(group_id) {
				const url = getApp().globalData.apiUrl + "/info/group"
				var that = this;
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"account": getApp().globalData.accountInfo.account,
						"cookie": getApp().globalData.accountInfo.cookie,
						"target": group_id
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						// console.log(result)
						if(result.code == 200){
							result = result.data
							result.avatar = result.avatar != null ? result.avatar : getApp().globalData.defaultAvatar
							that.groupInfo = result
						}else if(result.code == 401){
							// 跳转登录
						}else if(result.code == 403){
							
						}else {
							
						}
					} 
				});
			},
			getGroupMember(group_id) {
				const url = getApp().globalData.apiUrl + "/info/groupMembers"
				var that = this;
				uni.request({
					url: url,
					method: 'GET',
					data: {
						"account": getApp().globalData.accountInfo.account,
						"cookie": getApp().globalData.accountInfo.cookie,
						"group_id": group_id
					},
					dataType:'json',
					success: (res) => {
						var result = res.data
						// console.log(result)
						if(result.code == 200){
							result = result.data
							that.groupMembers.push(result.owner) 
							that.id_to_avatar[result.owner.user_id] = result.owner.avatar != null ? result.owner.avatar : getApp().globalData.defaultAvatar
							for (var i=0;i<result.admin.length;i++) {
								that.id_to_avatar[result.admin[i].user_id] = result.admin[i].avatar != null ? result.admin[i].avatar : getApp().globalData.defaultAvatar
								that.groupMembers.push(result.admin[i])
							}
							for (var i=0;i<result.member.length;i++) {
								that.id_to_avatar[result.member[i].user_id] = result.member[i].avatar != null ? result.member[i].avatar : getApp().globalData.defaultAvatar
								that.groupMembers.push(result.member[i])
							}
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
	.margin-top-bottom {
		margin-top: 20rpx;
		margin-bottom: 20rpx;
	}
	.uni-lastmsg {
		text-overflow: ellipsis;
		overflow: hidden;
		white-space: nowrap;
	}
	.no-wrap {
		flex-wrap:nowrap;
	}
</style>
