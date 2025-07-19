const UserForm = ({ name, setName, phone, setPhone }) => {
  return (
    <div className="w-4/5 mx-auto flex flex-col main-text">
      <img src="/logo_text.png" alt="logo" className="w-1/2 mx-auto" />

      <h1 className="text-center my-[52px]">Please Complete Your Data</h1>

      <div className="flex flex-col items-center justify-center gap-y-[54px]">
        <div className="w-full">
          <label>Name</label>
          <input
            className="border-2 border-black rounded-3xl w-full height-input px-10"
            type="text"
            id="name"
            name="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className="w-full">
          <label>Phone Number</label>
          <input
            className="border-2 border-black rounded-3xl w-full height-input px-10"
            type="number"
            id="phone"
            name="phone"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
          />
        </div>
      </div>
    </div>
  );
};

export default UserForm;
