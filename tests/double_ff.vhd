library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

-- Used to reduce metastability with asyncronous inputs or clock domain crossings
entity double_ff is
    port(
        clock : in std_logic;
        sig_in : in std_logic;
        sig_out : out std_logic
        );
end;

architecture behavioral of double_flip_flop is
    signal in_reg : std_logic;
    signal out_reg : std_logic;
    signal in_next : std_logic;
    signal out_next : std_logic;

begin
    -- registers
    process(clock)
    begin
        if rising_edge(clock) then
            in_reg <= in_next;
            out_reg <= out_next;
        end if; -- rising edge clock
    end process;
    -- next state
    in_next <= sig_in;
    out_next <= in_reg;
    -- output
    sig_out <= out_reg;
end behavioral;
