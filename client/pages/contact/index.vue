<template>
	<view>
		<view class="cu-list menu-avatar no-padding">
			<view class="cu-item" v-for="(item,index) in list" :key="index" @click="goToDetail(item.user_id)">
				<view class="cu-avatar lg radius"  :style="{backgroundImage:'url(' + item.avatar + ')'}"></view>
				<view class="content">
					<view class="text-grey">{{ item.nickname }}</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				StatusBar: this.StatusBar,
				CustomBar: this.CustomBar,
				hidden: true,
				listCurID: '',
				list: [],
			};
		},
		onLoad() {
			this.getFriends()
		},
		onReady() {
			let that = this;
		},
		methods: {
			//获取文字信息
			getCur(e) {
				this.hidden = false;
				this.listCur = this.list[e.target.id].name;
			},
			setCur(e) {
				this.hidden = true;
				this.listCur = this.listCur
			},
			//滑动选择Item
			tMove(e) {
				let y = e.touches[0].clientY,
					offsettop = this.boxTop,
					that = this;
				//判断选择区域,只有在选择区才会生效
				if (y > offsettop) {
					let num = parseInt((y - offsettop) / 20);
					this.listCur = that.list[num].name
				};
			},

			//触发全部开始选择
			tStart() {
				this.hidden = false
			},

			//触发结束选择
			tEnd() {
				this.hidden = true;
				this.listCurID = this.listCur
			},
			indexSelect(e) {
				let that = this;
				let barHeight = this.barHeight;
				let list = this.list;
				let scrollY = Math.ceil(list.length * e.detail.y / barHeight);
				for (let i = 0; i < list.length; i++) {
					if (scrollY < i + 1) {
						that.listCur = list[i].name;
						that.movableY = i * 20
						return false
					}
				}
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
						console.log(result)
						if(result.code == 200){
							result = result.data
							for (var i=0;i<result.length;i++) {
								if (result[i].avatar == null) result[i].avatar = getApp().globalData.defaultAvatar
							}
							that.list = result;
						}else if(result.code == 401){
							// 跳转登录
						}else if(result.code == 403){
							
						}else {
							
						}
					}
				});
			},
			goToDetail(user_id) {
				uni.navigateTo({
					url: "./detail?user_id=" + user_id
				})
			}
		}
	}
</script>

<style>
	.indexBar {
		position: fixed;
		right: 0px;
		bottom: 0px;
		padding: 20upx 20upx 20upx 60upx;
		display: flex;
		align-items: center;
	}
	
	.indexBar .indexBar-box {
		width: 40upx;
		height: auto;
		background: #fff;
		display: flex;
		flex-direction: column;
		box-shadow: 0 0 20upx rgba(0, 0, 0, 0.1);
		border-radius: 10upx;
	}
	
	.indexBar-item {
		flex: 1;
		width: 40upx;
		height: 40upx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 24upx;
		color: #888;
	}
	
	movable-view.indexBar-item {
		width: 40upx;
		height: 40upx;
		z-index: 9;
		position: relative;
	}
	
	movable-view.indexBar-item::before {
		content: "";
		display: block;
		position: absolute;
		left: 0;
		top: 10upx;
		height: 20upx;
		width: 4upx;
		background-color: #f37b1d;
	}
	
	.indexToast {
		position: fixed;
		top: 0;
		right: 80upx;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		width: 100upx;
		height: 100upx;
		border-radius: 10upx;
		margin: auto;
		color: #fff;
		line-height: 100upx;
		text-align: center;
		font-size: 48upx;
	}
</style>
