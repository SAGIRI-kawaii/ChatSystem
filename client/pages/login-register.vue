<template>
	<view>
		<form>
			<view class="cu-form-group">
				<view class="title cuIcon-people"></view>
				<input placeholder="请输入用户名" name="input" v-model="username"></input>
			</view>
			<view class="cu-form-group">
				<view class="title cuIcon-lock"></view>
				<input placeholder="请输入密码" name="input" v-model="password"></input>
			</view>
		</form>
		<view class="padding flex flex-direction">
			<button class="cu-btn bg-green lg" @click="login">注册/登录</button>
		</view>
		<view class="flex solid-top padding justify-center">
			<view>若您还没有账号自会自动帮您注册</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				username: "",
				password: ""
			}
		},
		methods: {
			login() {
				const url = getApp().globalData.apiUrl + "/user/login/?username=" + this.username + "&password=" + this.password
				var that = this
				uni.request({
					url: url,
					header: {'content-type': 'application/x-www-form-urlencoded'},
					method: 'POST',
					data: {
						username: that.username,
						password: that.password
					},
					dataType:'json',
					success: (res) => {
						var result = res.data;
						console.log(result)
						if(result.code == 200){
							getApp().globalData.accountInfo.account = result.data.user_id
							getApp().globalData.accountInfo.cookie = result.data.cookie
							getApp().globalData.accountInfo.avatar = result.data.avatar
							uni.showToast({
								title: "登录成功！即将返回首页！",
								icon: "none"
							});
							getApp().globalData.getChatData();
							getApp().globalData.getFriends();
							getApp().globalData.getGroups();
							getApp().globalData.initWebSocket()
							uni.navigateBack({
								animationDuration: 1000
							})
						}else if(result.code == 402){
							that.register()
						}else if(result.code == 403){
							uni.showToast({
								title: "用户名或密码错误！",
								icon: "none"
							});
						}else if(result.code == 404){
							Toast.fail("服务器错误")
						}
					} 
				}); 
			},
			register() {
				const url = getApp().globalData.apiUrl + "/user/register/?username=" + this.username + "&password=" + this.password
				var that = this
				uni.request({
					url: url,
					header: {'content-type': 'application/x-www-form-urlencoded'},
					method: 'POST',
					data: {
						username: that.username,
						password: that.password
					},
					dataType:'json',
					success: (res) => {
						var result = res.data;
						console.log(result)
						if(result.code == 201){
							getApp().globalData.accountInfo.account = result.data.user_id
							getApp().globalData.accountInfo.cookie = result.data.cookie
							getApp().globalData.accountInfo.avatar = result.data.avatar
							getApp().globalData.initWebSocket()
							uni.showToast({
								title: "登录成功！即将返回首页！",
								icon: "none"
							});
							getApp().globalData.getChatData();
							getApp().globalData.getFriends();
							getApp().globalData.getGroups();
							// uni.redirectTo({
							// 	url: "/pages/index/index"
							// })
							uni.navigateBack({
								animationDuration: 1000
							})
						}else if(result.code == 403){
							uni.showToast({
								title: "用户名已存在！",
								icon: "none"
							});
						}else if(result.code == 500){
							Toast.fail("服务器错误")
						}
					} 
				}); 
			}
		}
	}
</script>

<style>
</style>
